"""Maze grid: layout, movement rules, line of sight, path distance."""
from collections import deque

import numpy as np

# '#' wall  '.' pellet  ' ' empty  'F' fly start  'G' ghost start  '-' ghost-house door (ghosts only)
LAYOUT = [
    "###################",
    "#........#........#",
    "#.##.###.#.###.##.#",
    "#.................#",
    "#.##.#.#####.#.##.#",
    "#....#...#...#....#",
    "####.###.#.###.####",
    "####.#...G...#.####",
    "####.#.##-##.#.####",
    "#......#GGG#......#",
    "####.#.#####.#.####",
    "####.#.......#.####",
    "####.#.#####.#.####",
    "#........#........#",
    "#.##.###.#.###.##.#",
    "#..#.....F.....#..#",
    "##.#.#.#####.#.#.##",
    "#....#...#...#....#",
    "#.######.#.######.#",
    "#.................#",
    "###################",
]

DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # up, right, down, left (x = column, y = row, y down)


class Maze:
    def __init__(self, layout=LAYOUT):
        self.h, self.w = len(layout), len(layout[0])
        self.grid = [list(r) for r in layout]
        self.fly_start = self._find("F")[0]
        self.ghost_starts = self._find("G")
        self.house = set(self.ghost_starts[1:]) | set(self._find("-"))
        self.pellet_template = set(self._find("."))
        self._los_cache = {}
        self.reset_pellets()

    def _find(self, ch):
        return [(x, y) for y, row in enumerate(self.grid) for x, c in enumerate(row) if c == ch]

    def reset_pellets(self):
        self.pellets = set(self.pellet_template)

    def open_for(self, x, y, ghost=False):
        if not (0 <= x < self.w and 0 <= y < self.h):
            return False
        c = self.grid[y][x]
        if c == "#":
            return False
        if (x, y) in self.house and not ghost:
            return False
        return True

    def exits(self, tile, ghost=False):
        return [d for d in DIRS if self.open_for(tile[0] + d[0], tile[1] + d[1], ghost)]

    def line_of_sight(self, a, b, step=0.2):
        """Walls block the straight line between tile centres nearest to a and b (cached: maze is static)."""
        key = (int(round(a[0])), int(round(a[1])), int(round(b[0])), int(round(b[1])))
        hit = self._los_cache.get(key)
        if hit is None:
            hit = self._los_cache[key] = self._line_of_sight(np.array(key[:2], float), np.array(key[2:], float), step)
        return hit

    def _line_of_sight(self, a, b, step):
        n = max(1, int(np.hypot(*(b - a)) / step))
        for t in np.linspace(0, 1, n + 1)[1:-1]:
            x, y = np.rint(a + (b - a) * t).astype(int)
            if self.grid[y][x] == "#":
                return False
        return True

    def path_distances(self, start):
        """BFS tile distances from `start` through open tiles (air travels along corridors)."""
        dist = {start: 0}
        q = deque([start])
        while q:
            x, y = q.popleft()
            for dx, dy in DIRS:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in dist and self.open_for(nx, ny, ghost=True):
                    dist[(nx, ny)] = dist[(x, y)] + 1
                    q.append((nx, ny))
        return dist


class Mover:
    """Moves tile-center to tile-center; `choose(mover)` picks a direction at each center."""

    def __init__(self, maze, tile, speed, ghost=False):
        self.maze, self.ghost = maze, ghost
        self.pos = np.array(tile, float)
        self.dir = (0, 0)
        self.speed = speed

    @property
    def tile(self):
        return (int(round(self.pos[0])), int(round(self.pos[1])))

    def at_center(self):
        return np.allclose(self.pos, np.rint(self.pos), atol=1e-6)

    def reverse(self):
        self.dir = (-self.dir[0], -self.dir[1])

    def update(self, dt, choose):
        remaining = self.speed * dt
        for _ in range(8):
            if remaining <= 1e-9:
                break
            if self.at_center():
                self.pos = np.rint(self.pos)
                new = choose(self)
                if new is not None:
                    self.dir = new
                tx, ty = self.tile[0] + self.dir[0], self.tile[1] + self.dir[1]
                if self.dir == (0, 0) or not self.maze.open_for(tx, ty, self.ghost):
                    self.dir = (0, 0)
                    return
            target = np.rint(self.pos) + np.array(self.dir) if self.at_center() else self._next_center()
            gap = np.abs(target - self.pos).sum()
            move = min(gap, remaining)
            self.pos = self.pos + np.array(self.dir) * move
            remaining -= move
            if move == gap:
                self.pos = np.rint(self.pos)

    def _next_center(self):
        d = np.array(self.dir, float)
        nxt = self.pos.copy()
        for i in range(2):
            if d[i] > 0:
                nxt[i] = np.floor(self.pos[i] + 1e-9) + 1
            elif d[i] < 0:
                nxt[i] = np.ceil(self.pos[i] - 1e-9) - 1
        return nxt
