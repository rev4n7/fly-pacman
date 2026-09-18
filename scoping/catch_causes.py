import sys, numpy as np, pandas as pd
from multiprocessing import Pool
from flypac.world import World
def run(args):
    readout, seed, speed = args
    w = World(readout=readout, ghost_speed=speed, seed=seed)
    for _ in range(int(180 / 0.02)):
        w.step()
    rows = []
    for e in w.log:
        if e["kind"] != "catch":
            continue
        tk = e["recent_takeoff"]
        if tk is None:
            cause = "GF fired but takeoff blocked (cooldown)" if e["gf_recent"] and e["in_cooldown"] else \
                    "GF fired <1s before but no takeoff" if e["gf_recent"] else "never noticed (no GF spike)"
        elif tk["toward_ghost"] > 0.3:
            cause = "jumped TOWARD the ghost"
        else:
            cause = "jumped away, still caught"
        rows.append(dict(readout=readout, seed=seed, cause=cause,
                         ghost_bearing_at_catch=abs(e["ghost_bearing"]) if e["ghost_bearing"] is not None else np.nan))
    tks = [e for e in w.log if e["kind"] == "takeoff"]
    rows.append(dict(readout=readout, seed=seed, cause="(pellets eaten)", n=w.stats.pellets))
    return rows, (readout, len(tks), float(np.mean([e["toward_ghost"] > 0.3 for e in tks])) if tks else 0.0)
if __name__ == "__main__":
    speed = float(sys.argv[1]) if len(sys.argv) > 1 else 3.0
    jobs = [(r, s, speed) for r in ["circuit", "eyes"] for s in range(4)]
    with Pool(8) as p:
        res = p.map(run, jobs)
    df = pd.DataFrame([r for rows, _ in res for r in rows])
    print(f"ghost speed {speed}: catches by cause (4 x 180 s each):")
    print(df.groupby(["readout", "cause"]).size().unstack(0, fill_value=0).to_string())
    print("\nmedian |ghost bearing| at catch (0=ahead, 180=behind):")
    print(df.groupby(["readout", "cause"]).ghost_bearing_at_catch.median().round(0).to_string())
    tk = pd.DataFrame([t for _, t in res], columns=["readout", "takeoffs", "frac_toward_ghost"])
    print("\n", tk.groupby("readout").agg(takeoffs=("takeoffs", "sum"), frac_toward_ghost=("frac_toward_ghost", "mean")).round(2))
