"""Reproduce: ghost ahead moving away, then U-turn. Does the fly react in time? Does it chase ghosts?"""
import sys, types, numpy as np, flypac.brain as B
T = types.SimpleNamespace(FRAME=0.02)
def _si(pos, vel):
    d = float(np.hypot(*pos))
    return dict(bearing=float(np.degrees(np.arctan2(pos[0], pos[1]))), dist=d, size=0.9, closing=float(-(pos @ vel) / max(d, 1e-6)), speed=float(np.hypot(*vel)), visible=True)
T.scene_input = _si
FR = T.FRAME
def uturn(b, gap, t_rev=0.4, seeds=4):
    out = []
    for s in range(seeds):
        b.rng = np.random.default_rng(s); b.reset()
        pos = np.array([0.0, gap]); gf = None
        for f in range(int(1.5 / FR)):
            t = f * FR
            vel = np.array([0, -0.5]) if t < t_rev else np.array([0, -6.5])  # relative velocity (fly 3.5 fwd, ghost 3)
            pos = pos + vel * FR
            b.sense([dict(T.scene_input(pos, vel), speed=3.0)])
            c = b.step(FR); m = b.motor(c)
            if gf is None and m["jump"]:
                gf = t
            if pos[1] < 0.6:
                out.append(("caught" if gf is None else f"GF {1000*(t-gf):.0f}ms before contact")); break
        else:
            out.append("no contact")
    return out
def chase(b):
    b.reset(); b.rng = np.random.default_rng(0)
    for d in [1.5, 2.5, 4.0]:
        b.reset(); b.sense([dict(bearing=35.0, dist=d, size=0.9, closing=0.0, speed=3.0, visible=True)])
        b.step(0.5); c = b.step(0.5)
        print(f"   stationary-distance ghost at 35 deg right, {d} tiles: turn_right = {b.motor(c)['turn_right']:+.1f} Hz (+ = turns TOWARD it)")
b = B.Brain(seed=0)
for pref in [15.0, 6.0]:
    B.SENSE["pursuit_pref_size"] = pref
    print(f"pursuit_pref_size={pref}"); chase(b)
B.SENSE["pursuit_pref_size"] = 6.0
for half in [1500, 800, 500]:
    B.SENSE["loom_half"] = half
    print(f"loom_half={half}")
    for gap in [1.5, 2.5, 3.5]:
        print(f"   gap {gap} tiles at U-turn:", uturn(b, gap))
