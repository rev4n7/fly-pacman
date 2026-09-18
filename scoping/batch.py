"""Headless batch: how the fly does per readout / hearing / ghost speed."""
import sys, itertools, numpy as np
from multiprocessing import Pool
from flypac.world import World
SECS = 120
def run(args):
    readout, hearing, speed, seed = args
    w = World(readout=readout, hearing=hearing, ghost_speed=speed, seed=seed)
    for _ in range(int(SECS / 0.02)):
        w.step()
    s = w.stats
    return args, s.pellets, s.jumps, s.escapes, s.catches
if __name__ == "__main__":
    speeds = [float(x) for x in sys.argv[1:]] or [2.5, 3.0]
    jobs = list(itertools.product(["circuit", "eyes"], [True, False], speeds, range(3)))
    with Pool(8) as p:
        res = p.map(run, jobs)
    import pandas as pd
    df = pd.DataFrame([(*a, *r) for a, *r in res], columns=["readout", "hearing", "ghost_speed", "seed", "pellets", "jumps", "survived", "caught"])
    g = df.groupby(["ghost_speed", "readout", "hearing"])[["pellets", "jumps", "survived", "caught"]].mean().round(1)
    g["survive_rate"] = (g.survived / g.jumps.clip(lower=0.1)).round(2)
    g["pellets_per_catch"] = (g.pellets / g.caught.clip(lower=0.5)).round(1)
    print(f"per {SECS}s of simulated play, mean of 3 seeds"); print(g.to_string())
