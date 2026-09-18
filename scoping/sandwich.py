import numpy as np, pandas as pd
from multiprocessing import Pool
from flypac.world import World
def run(a):
    speed, n_ghosts, seed = a
    w = World(readout="eyes", ghost_speed=speed, n_ghosts=n_ghosts, seed=seed)
    for _ in range(int(180 / 0.02)): w.step()
    same = diff = none = 0
    for e in w.log:
        if e["kind"] != "catch": continue
        tk = e["recent_takeoff"]
        if tk is None: none += 1
        elif tk["ghost_id"] == e["catcher"]: same += 1
        else: diff += 1
    return dict(ghost_speed=speed, ghosts=n_ghosts, pellets=w.stats.pellets, jumps=w.stats.jumps,
                caught=w.stats.catches, same_ghost=same, other_ghost=diff, no_takeoff=none)
if __name__ == "__main__":
    jobs = [(sp, n, s) for sp in [3.0, 2.5, 2.0] for n in [4, 3] for s in range(3)]
    with Pool(8) as p: res = p.map(run, jobs)
    df = pd.DataFrame(res).groupby(["ghost_speed", "ghosts"]).mean(numeric_only=True).drop(columns=[]).round(1)
    df["secs_per_catch"] = (180 / df.caught.clip(lower=0.3)).round(0)
    print("eyes readout, per 180 s, mean of 3 seeds"); print(df.to_string())
