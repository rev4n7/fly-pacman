"""Game logic without graphics: maze, ghosts, and a fly driven only by the brain.

No player input and no "if ghost near then flee" rule. Every tick:
  scene -> brain.sense() -> brain.step() -> motor readout -> fly movement
"""
from collections import deque
from dataclasses import dataclass

import numpy as np

from . import brain as B
from .maze import DIRS, Maze, Mover

FRAME = 0.02            # s of simulated time per tick

# ---- DESIGN: body / game constants ----
FLY_WALK = 3.5          # tiles/s
FLY_JUMP = 9.0          # tiles/s during an escape burst
JUMP_TIME = 0.35        # s of burst after takeoff
JUMP_COOLDOWN = 0.0     # s after a burst before the next takeoff (real GF can re-trigger at once)
COMMIT_DELAY = 0.0      # s from Giant Fiber spike to takeoff (GF short-mode takeoffs take a few ms)
DIR_WINDOW = 0.3        # s of descending-neuron activity used to set takeoff direction
STEER_GAIN = 0.05       # body-frame turn per Hz of DNa02 R-L difference
GHOST_SIZE = 0.9        # tiles
PELLET_SIZE = 0.25      # tiles
PELLET_VIEW = 6.0       # tiles; farther pellets are sub-pixel to a fly and skipped for speed
CATCH_DIST = 0.6        # tiles
SCATTER, CHASE = 5.0, 15.0
CORNERS = [(1, 1), (17, 1), (1, 19), (17, 19)]


def right_of(h):
    return np.array([-h[1], h[0]], float)  # y points down, so this is the fly's right


@dataclass
class Stats:
    time: float = 0.0
    pellets: int = 0
    jumps: int = 0
    escapes: int = 0
    catches: int = 0
    rounds: int = 1


class Ghost(Mover):
    def __init__(self, maze, index, speed):
        super().__init__(maze, maze.ghost_starts[index], speed, ghost=True)
        self.index = index
        self.release = 1.5 * index
        self.prev_dist = None
        self.left_house = index == 0
        self.ghost = not self.left_house  # may pass the house door only until it has left

    def choose_for(self, world):
        def choose(m):
            tile = m.tile
            if not self.left_house and tile == (9, 7):
                self.left_house = True
                m.ghost = False
            exits = m.maze.exits(tile, ghost=not self.left_house)
            back = (-m.dir[0], -m.dir[1])
            options = [d for d in exits if d != back] or exits
            if not self.left_house:
                target = (9, 7)
            elif world.ghost_mode() == "scatter":
                target = CORNERS[self.index % 4]
            else:
                target = world.chase_target(self.index)
            return min(options, key=lambda d: (tile[0] + d[0] - target[0]) ** 2 + (tile[1] + d[1] - target[1]) ** 2)
        return choose


class World:
    def __init__(self, n_ghosts=4, ghost_speed=2.0, readout="eyes", hearing=True, seed=0):
        self.rng = np.random.default_rng(seed)
        self.maze = Maze()
        self.brain = B.Brain(seed=seed)
        self.n_ghosts, self.ghost_speed = n_ghosts, ghost_speed
        self.readout = readout
        self.set_hearing(hearing)
        self.stats = Stats()
        self.log = []                  # takeoff / catch events for diagnostics
        n = self.brain.neurons
        self.loom_cos = np.cos(np.radians(self.brain.body_az[self.brain.loom]))
        self.side_idx = {s: [self.brain.out[f"{t}_{s}"] for t in ["DNp01", "DNp02", "DNp04", "DNp11"]] for s in "LR"}
        self.n_neurons, self.n_synapses = len(n), int(self.brain.edges.weight.sum())
        self.reset_round()

    # ------------------------------------------------------------------ setup
    def set_hearing(self, on):
        self.hearing = on
        B.SENSE["hear_rate_max"] = 80.0 if on else 0.0

    def reset_round(self):
        self.fly = Mover(self.maze, self.maze.fly_start, FLY_WALK)
        self.heading = np.array([-1.0, 0.0])
        self.ghosts = [Ghost(self.maze, i, self.ghost_speed) for i in range(self.n_ghosts)]
        self.round_time = 0.0
        self.pause = 0.0
        self.brain.reset()
        self.hist = deque(maxlen=int(DIR_WINDOW / FRAME))
        self.counts = np.zeros(self.brain.N, dtype=np.int32)
        self.pending_takeoff = None
        self.escape_until = -1.0
        self.cooldown_until = -1.0
        self.escape_dir = None
        self.last_takeoff = None       # (time, body-frame fwd, right)
        self.survive_check = None
        self.event = ""
        self.event_time = -10.0
        self.ghost_inputs = []
        self.last_gf_time = None

    # ------------------------------------------------------------------ ghosts
    def ghost_mode(self):
        return "scatter" if (self.round_time % (SCATTER + CHASE)) < SCATTER else "chase"

    def chase_target(self, i):
        ft = np.array(self.fly.tile)
        h = np.rint(self.heading).astype(int)
        if i == 0:
            t = ft
        elif i == 1:
            t = ft + 4 * h
        elif i == 2:
            t = 2 * (ft + 2 * h) - np.array(self.ghosts[0].tile)
        else:
            t = ft if np.hypot(*(ft - np.array(self.ghosts[i].tile))) > 6 else np.array(CORNERS[3])
        return tuple(t)

    # ------------------------------------------------------------------ senses
    def sense(self):
        fp, h = self.fly.pos, self.heading
        r = right_of(h)
        paths = self.maze.path_distances(self.fly.tile)
        ghosts = []
        for g in self.ghosts:
            rel = g.pos - fp
            d = float(np.hypot(*rel))
            closing = 0.0 if g.prev_dist is None else (g.prev_dist - d) / FRAME
            g.prev_dist = d
            moving = g.dir != (0, 0) and self.round_time >= g.release
            ghosts.append(dict(
                bearing=float(np.degrees(np.arctan2(rel @ r, rel @ h))), dist=d, size=GHOST_SIZE,
                closing=closing, speed=g.speed if moving else 0.0,
                visible=self.maze.line_of_sight(fp, g.pos),
                hear_dist=max(d, float(paths.get(g.tile, 99)))))
        pellets = []
        for p in self.maze.pellets:
            rel = np.array(p, float) - fp
            d = float(np.hypot(*rel))
            if d > PELLET_VIEW or d < 0.3:
                continue
            if not self.maze.line_of_sight(fp, p):
                continue
            pellets.append(dict(bearing=float(np.degrees(np.arctan2(rel @ r, rel @ h))), dist=d,
                                size=PELLET_SIZE, visible=True))
        self.ghost_inputs = ghosts
        self.brain.sense(ghosts, pellets)

    # ------------------------------------------------------------------ motor
    def escape_vector(self):
        """Body-frame (fwd, right) takeoff direction read from the simulated neurons."""
        w = np.sum(self.hist, axis=0) if self.hist else self.counts
        o = self.brain.out
        side_l, side_r = w[self.side_idx["L"]].sum(), w[self.side_idx["R"]].sum()
        right = (side_l - side_r) / (side_l + side_r + 1.0)          # away from the more active side
        if self.readout == "circuit":
            p11 = w[o["DNp11_L"]] + w[o["DNp11_R"]]
            p02 = w[o["DNp02_L"]] + w[o["DNp02_R"]]
            fwd = (p11 - p02) / (p11 + p02 + 1.0)                     # rear-threat DN vs front-threat DN
        else:  # "eyes": which real looming cells fired, weighted by where each one looks
            lc = w[self.brain.loom]
            fwd = -(lc @ self.loom_cos) / (lc.sum() + 1.0)
        return float(fwd), float(right)

    def choose_fly(self, m):
        tile = m.tile
        exits = self.maze.exits(tile)
        if not exits:
            return (0, 0)
        if self.escape_dir is not None and self.escape_dir in exits:
            d, self.escape_dir = self.escape_dir, None
            self.heading = np.array(d, float)
            return d
        motor = self.motor
        h, r = self.heading, right_of(self.heading)
        want = h + STEER_GAIN * motor["turn_right"] * r
        back = (-int(round(h[0])), -int(round(h[1])))
        options = [d for d in exits if d != back] or exits
        d = max(options, key=lambda d: np.dot(want, d) + 1e-6 * self.rng.random())
        self.heading = np.array(d, float)
        return d

    def nearest_ghost(self):
        if not self.ghost_inputs:
            return None
        return min(self.ghost_inputs, key=lambda g: g["dist"])

    def takeoff(self):
        fwd, right = self.escape_vector()
        g = self.nearest_ghost()
        if g is not None:
            a = np.radians(g["bearing"])
            toward = fwd * np.cos(a) + right * np.sin(a)   # >0 means the chosen direction points at the ghost
            self.log.append(dict(kind="takeoff", t=self.stats.time, fwd=fwd, right=right, ghost_bearing=g["bearing"],
                                 ghost_id=self.ghost_inputs.index(g), heading_before=tuple(self.heading),
                                 at_center=self.fly.at_center(),
                                 ghost_dist=g["dist"], toward_ghost=float(toward)))
        self.last_takeoff = (self.stats.time, fwd, right)
        self.fly.speed = FLY_JUMP
        self.escape_until = self.stats.time + JUMP_TIME
        self.cooldown_until = self.escape_until + JUMP_COOLDOWN
        want = fwd * self.heading + right * right_of(self.heading)
        if np.hypot(*want) < 0.05:
            want = self.heading.copy()
        if self.fly.at_center():
            exits = self.maze.exits(self.fly.tile) or [tuple(np.rint(self.heading).astype(int))]
            best = max(exits, key=lambda d: np.dot(want, d))
            self.fly.dir = best
            self.heading = np.array(best, float)
        else:
            if np.dot(want, self.heading) < 0:
                self.fly.reverse()
                self.heading = -self.heading
            lateral = [d for d in DIRS if abs(np.dot(d, self.heading)) < 0.5]
            best_lat = max(lateral, key=lambda d: np.dot(want, d))
            if np.dot(want, best_lat) > abs(np.dot(want, self.heading)):
                self.escape_dir = best_lat
        self.survive_check = self.stats.time + 2.0
        self.stats.jumps += 1
        self.flash("GIANT FIBER FIRED - TAKEOFF")

    def flash(self, text):
        self.event, self.event_time = text, self.stats.time

    # ------------------------------------------------------------------ tick
    def step(self):
        dt = FRAME
        self.stats.time += dt
        if self.pause > 0:
            self.pause -= dt
            if self.pause <= 0:
                self.reset_round()
            return
        self.round_time += dt
        t = self.stats.time

        self.sense()
        self.counts = self.brain.step(dt)
        self.hist.append(self.counts)
        self.motor = self.brain.motor(self.counts)

        if self.motor["jump"]:
            self.last_gf_time = t
        if self.motor["jump"] and self.pending_takeoff is None and t >= self.cooldown_until:
            self.pending_takeoff = t + COMMIT_DELAY
        if self.pending_takeoff is not None and t >= self.pending_takeoff:
            self.pending_takeoff = None
            self.takeoff()
            if self.log and self.log[-1]["kind"] == "takeoff":
                self.log[-1]["heading_after"] = tuple(self.heading)
        if t >= self.escape_until:
            self.fly.speed = FLY_WALK

        self.fly.update(dt, self.choose_fly)
        if self.fly.dir != (0, 0):
            self.heading = np.array(self.fly.dir, float)

        ft = self.fly.tile
        if ft in self.maze.pellets and np.hypot(*(self.fly.pos - ft)) < 0.35:
            self.maze.pellets.discard(ft)
            self.stats.pellets += 1
            if not self.maze.pellets:
                self.maze.reset_pellets()
                self.stats.rounds += 1

        for g in self.ghosts:
            if self.round_time >= g.release:
                g.update(dt, g.choose_for(self))
            if np.hypot(*(g.pos - self.fly.pos)) < CATCH_DIST:
                gi = self.nearest_ghost()
                takeoffs = [e for e in self.log if e["kind"] == "takeoff" and t - e["t"] < 1.0]
                self.log.append(dict(kind="catch", t=t, ghost_bearing=gi["bearing"] if gi else None,
                                     catcher=self.ghosts.index(g), heading=tuple(self.heading), fly_pos=tuple(self.fly.pos),
                                     ghost_dir=g.dir,
                                     gf_recent=self.last_gf_time is not None and t - self.last_gf_time < 1.0,
                                     in_cooldown=t < self.cooldown_until, escaping=t < self.escape_until,
                                     recent_takeoff=takeoffs[-1] if takeoffs else None))
                self.stats.catches += 1
                self.survive_check = None
                self.flash("CAUGHT")
                self.pause = 1.2
                return

        if self.survive_check is not None and t >= self.survive_check:
            self.survive_check = None
            self.stats.escapes += 1
