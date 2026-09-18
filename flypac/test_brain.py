"""Standalone brain test: fake Pac-Man scenes, no game.

Run:  .venv\\Scripts\\python -m flypac.test_brain [--exclude-lc-recurrence]

The fly sits at the origin facing +y. Each scene moves a ghost (or shows a pellet) and we
record what the real circuit does: when the Giant Fiber first fires, which escape
direction the descending neurons encode, and how the steering neurons respond.
"""
import argparse

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from . import brain as B
from . import config as C

FRAME = 0.02  # s between sensory updates (a 50 fps game)
GHOST_SIZE = 0.9


def ghost_path(start, velocity):
    start, velocity = np.asarray(start, float), np.asarray(velocity, float)
    return lambda t: (start + velocity * t, velocity)


def scene_input(pos, vel, visible=True):
    d = float(np.hypot(*pos))
    return dict(bearing=float(np.degrees(np.arctan2(pos[0], pos[1]))), dist=d, size=GHOST_SIZE,
                closing=float(-(pos @ vel) / max(d, 1e-6)), speed=float(np.hypot(*vel)), visible=visible)


SCENES = {
    "idle": dict(duration=1.5),
    "head-on (ghost ahead)": dict(ghost=ghost_path([0, 10], [0, -4]), duration=2.6),
    "from behind, eyes+ears": dict(ghost=ghost_path([0, -10], [0, 4]), duration=2.6),
    "from behind, eyes only": dict(ghost=ghost_path([0, -10], [0, 4]), duration=2.6, deaf=True),
    "from the left": dict(ghost=ghost_path([-10, 0], [4, 0]), duration=2.6),
    "from the right": dict(ghost=ghost_path([10, 0], [-4, 0]), duration=2.6),
    "passing sideways": dict(ghost=ghost_path([-6, 2.5], [4, 0]), duration=3.0),
    "hidden behind wall": dict(ghost=ghost_path([0, 10], [0, -4]), duration=2.6, occluded=True),
    "pellets on the left": dict(pellets=[(-45, 2.0), (-35, 3.0), (-50, 4.0)], duration=1.5),
    "pellets on the right": dict(pellets=[(45, 2.0), (35, 3.0), (50, 4.0)], duration=1.5),
}


def run(brain, spec):
    brain.reset()
    hear_max = B.SENSE["hear_rate_max"]
    if spec.get("deaf"):
        B.SENSE["hear_rate_max"] = 0.0
    n_frames = int(spec["duration"] / FRAME)
    keys = ["DNp01_L", "DNp01_R", "DNp02_L", "DNp02_R", "DNp11_L", "DNp11_R", "DNa02_L", "DNa02_R"]
    trace = {k: np.zeros(n_frames) for k in keys + ["dist", "loom_in"]}
    first_jump = None
    motor_at_jump = None
    try:
        for f in range(n_frames):
            t = f * FRAME
            ghosts, pellets = [], []
            if "ghost" in spec:
                pos, vel = spec["ghost"](t)
                ghosts.append(scene_input(pos, vel, visible=not spec.get("occluded")))
                trace["dist"][f] = ghosts[0]["dist"]
            for bearing, dist in spec.get("pellets", []):
                pellets.append(dict(bearing=bearing, dist=dist, size=0.25, visible=True))
            brain.sense(ghosts, pellets)
            counts = brain.step(FRAME)
            m = brain.motor(counts)
            for k in keys:
                trace[k][f] = brain.rates[brain.out[k]]
            trace["loom_in"][f] = brain.input_rate[brain.loom].mean()
            if m["jump"] and first_jump is None:
                first_jump = t
                motor_at_jump = m
                motor_at_jump["dist"] = trace["dist"][f]
    finally:
        B.SENSE["hear_rate_max"] = hear_max
    return trace, first_jump, motor_at_jump, m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exclude-lc-recurrence", action="store_true")
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()
    brain = B.Brain(seed=args.seed, exclude_lc_recurrence=args.exclude_lc_recurrence)

    fig, axes = plt.subplots(len(SCENES), 1, figsize=(10, 2.1 * len(SCENES)), sharex=True)
    print(f"{'scene':26s} {'GF fires at':>12s} {'ghost dist':>10s} {'GF L/R spikes':>13s} "
          f"{'escape: fwd(+)/back(-)':>22s} {'right(+)/left(-)':>16s} {'steer right(+)':>14s}")
    for ax, (name, spec) in zip(axes, SCENES.items()):
        trace, t_jump, mj, m_end = run(brain, spec)
        if t_jump is None:
            print(f"{name:26s} {'no jump':>12s} {'':>10s} {'':>13s} {'':>22s} {'':>16s} {m_end['turn_right']:14.1f}")
        else:
            print(f"{name:26s} {t_jump:11.2f}s {mj['dist']:9.2f}t {str(mj['gf_spikes']):>13s} "
                  f"{mj['away_fwd']:22.1f} {mj['away_right']:16.1f} {mj['turn_right']:14.1f}")
        t = np.arange(len(trace["dist"])) * FRAME
        for k, col in [("DNp01", "k"), ("DNp02", "tab:red"), ("DNp11", "tab:blue"), ("DNa02", "tab:green")]:
            ax.plot(t, trace[k + "_L"], color=col, lw=1.2, label=k + " L")
            ax.plot(t, trace[k + "_R"], color=col, lw=1.2, ls="--", label=k + " R")
        if t_jump is not None:
            ax.axvline(t_jump, color="orange", lw=2)
        ax.set_title(name, loc="left", fontsize=9)
        ax.set_ylabel("Hz")
    axes[0].legend(ncol=8, fontsize=7, loc="upper right")
    axes[-1].set_xlabel("time (s)   orange line = first Giant Fiber spike (jump)")
    fig.tight_layout()
    out = C.DATA_DIR / ("brain_test_exclLC.png" if args.exclude_lc_recurrence else "brain_test.png")
    fig.savefig(out, dpi=90)
    print("figure:", out)


if __name__ == "__main__":
    main()
