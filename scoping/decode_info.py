"""Is front/back threat information present in the circuit's output neurons at all?
Held-out-bearing cross-validated logistic regression (numpy only)."""
import numpy as np, flypac.brain as B, flypac.test_brain as T
B.SENSE["hear_rate_max"] = 0.0; B.SENSE["loom_half"] = 1500; B.ADAPT_B = 0.0
b = B.Brain(seed=0); o = b.out; n = b.neurons

def fit_logreg(X, y, lam=1.0, iters=3000, lr=0.1):
    mu, sd = X.mean(0), X.std(0) + 1e-9; Z = (X - mu) / sd
    w = np.zeros(Z.shape[1]); c = 0.0
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(Z @ w + c)))
        w -= lr * (Z.T @ (p - y) / len(y) + lam * w / len(y)); c -= lr * np.mean(p - y)
    return lambda Xn: (((Xn - mu) / sd) @ w + c) > 0, w / sd

X, y, groups = [], [], []
for bearing in range(0, 360, 15):
    fb = -np.cos(np.radians(bearing))
    if abs(fb) < 0.3: continue
    for trial in range(6):
        b.rng = np.random.default_rng(7919 * bearing + trial); b.reset()
        th = np.radians(bearing); start = 10 * np.array([np.sin(th), np.cos(th)]); vel = -start / 10 * 4
        hist, t_gf = [], None
        for f in range(int(2.6 / T.FRAME)):
            pos = start + vel * f * T.FRAME
            b.sense([T.scene_input(pos, vel)]); c = b.step(T.FRAME); hist.append(c)
            if t_gf is None and (c[o["DNp01_L"]] + c[o["DNp01_R"]]) > 0: t_gf = f
            if t_gf is not None and f >= t_gf + 5: break
        if t_gf is None: continue
        X.append(np.sum(hist[max(0, t_gf - 15):], axis=0)); y.append(float(fb > 0)); groups.append(bearing)
X = np.log1p(np.array(X, float)); y = np.array(y); groups = np.array(groups)
roles = n.role.to_numpy()
sets = {
    "escape DNs (DNp01/02/04/06/11, TTMn, PSI)": np.flatnonzero(roles == "out_escape"),
    "escape DNs + GF middle layer": np.flatnonzero(np.isin(roles, ["out_escape", "middle_gf"])),
    "looming sensors themselves (upper bound)": np.flatnonzero(roles == "sense_looming"),
}
print(f"{len(y)} trials, {y.mean():.0%} labelled 'threat behind -> jump forward'")
folds = np.array_split(np.unique(groups), 6)
for name, cols in sets.items():
    correct = 0
    for held in folds:
        te = np.isin(groups, held)
        pred, _ = fit_logreg(X[~te][:, cols], y[~te])
        correct += np.sum(pred(X[te][:, cols]) == y[te])
    print(f"  {name:45s} features={len(cols):4d}  held-out-bearing accuracy {correct/len(y):.0%}")
cols = sets["escape DNs (DNp01/02/04/06/11, TTMn, PSI)"]
_, w = fit_logreg(X[:, cols], y)
for wi, i in sorted(zip(w, cols), key=lambda t: -abs(t[0])):
    print(f"    {n.type.iloc[i]:6s} {n.side.iloc[i]}  weight {wi:+.2f}  (+ = threat behind)")
