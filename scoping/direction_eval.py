"""How reliably does the real circuit's output encode which way to escape?"""
import sys, numpy as np, flypac.brain as B, flypac.test_brain as T
B.SENSE["hear_rate_max"] = 0.0
B.SENSE["loom_half"] = float(sys.argv[2]) if len(sys.argv) > 2 else 1500
B.ADAPT_B = float(sys.argv[1])
b = B.Brain(seed=0); o = b.out
PRE, POST = 0.3, float(sys.argv[3]) if len(sys.argv) > 3 else 0.06
res = []
for bearing in range(0, 360, 30):
    for trial in range(4):
        b.rng = np.random.default_rng(1000 * bearing + trial); b.reset()
        th = np.radians(bearing); start = 10 * np.array([np.sin(th), np.cos(th)]); vel = -start / 10 * 4
        hist, t_gf, d_gf = [], None, None
        for f in range(int(2.6 / T.FRAME)):
            pos = start + vel * f * T.FRAME
            b.sense([T.scene_input(pos, vel)]); c = b.step(T.FRAME); hist.append(c)
            if t_gf is None and (c[o["DNp01_L"]] + c[o["DNp01_R"]]) > 0:
                t_gf, d_gf = f, np.hypot(*pos)
            if t_gf is not None and f >= t_gf + POST / T.FRAME:
                break
        if t_gf is None:
            res.append((bearing, None, 0, 0)); continue
        w = np.sum(hist[max(0, t_gf - int(PRE / T.FRAME)):], axis=0)
        fwd = (w[o["DNp11_L"]] + w[o["DNp11_R"]]) - (w[o["DNp02_L"]] + w[o["DNp02_R"]])
        side = lambda s: sum(w[o[f"{k}_{s}"]] for k in ["DNp01", "DNp02", "DNp04", "DNp11"])
        res.append((bearing, d_gf, fwd, side("L") - side("R")))
print(f"adapt={B.ADAPT_B} loom_half={B.SENSE['loom_half']} POST={POST}")
print(" bearing  jumps  mean dist   fwd/back correct   left/right correct   (fwd, right) per trial")
ok_fb = ok_lr = n_fb = n_lr = 0
for bearing in range(0, 360, 30):
    rows = [r for r in res if r[0] == bearing and r[1] is not None]
    want_fwd = -np.cos(np.radians(bearing)); want_right = -np.sin(np.radians(bearing))
    fb = [np.sign(r[2]) == np.sign(want_fwd) for r in rows] if abs(want_fwd) > 0.3 else []
    lr = [np.sign(r[3]) == np.sign(want_right) for r in rows] if abs(want_right) > 0.3 else []
    ok_fb += sum(fb); n_fb += len(fb); ok_lr += sum(lr); n_lr += len(lr)
    dist = np.mean([r[1] for r in rows]) if rows else float("nan")
    print(f"  {bearing:4d}   {len(rows)}/4    {dist:5.2f}      {sum(fb)}/{len(fb)}               {sum(lr)}/{len(lr)}          "
          + " ".join(f"({r[2]:+d},{r[3]:+d})" for r in rows))
print(f"TOTAL fwd/back {ok_fb}/{n_fb} = {ok_fb/max(n_fb,1):.0%}   left/right {ok_lr}/{n_lr} = {ok_lr/max(n_lr,1):.0%}")
