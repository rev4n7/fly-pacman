import sys, numpy as np, flypac.brain as B, flypac.test_brain as T
b = B.Brain(seed=0)
for thr in [0.5, 1.0, 2.0, 4.0]:
    B.SENSE["hear_threshold"] = thr; out = []
    for name in ["from behind, eyes+ears", "from behind, eyes only", "hidden behind wall", "passing sideways", "idle"]:
        ds = []
        for trial in range(3):
            b.rng = np.random.default_rng(trial); _, tj, mj, _ = T.run(b, T.SCENES[name])
            ds.append(None if tj is None else round(float(mj["dist"]), 2))
        out.append(f"{name}: {ds}")
    print(f"threshold={thr}:  " + " | ".join(out))
