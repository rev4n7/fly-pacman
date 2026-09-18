import os; os.environ["SDL_VIDEODRIVER"] = "dummy"
import numpy as np, pygame, flypac.brainview as BV
from flypac.world import World
pygame.init(); pygame.display.set_mode((10, 10))
w = World(seed=0)
R, K, T = [], [], []
while w.stats.time < 60:
    w.step(); R.append(w.brain.rates.copy()); K.append(w.counts.copy()); T.append(w.stats.time)
R = np.array(R); K = np.array(K)
loom = R[:, w.brain.loom].mean(1)
gf = K[:, [w.brain.out["DNp01_L"], w.brain.out["DNp01_R"]]].sum(1)
cand = np.flatnonzero(gf > 0)
peak = cand[np.argmax(loom[cand])] if len(cand) else int(np.argmax(loom))
print("peak frame", peak, "t=%.2f" % T[peak], "loom mean %.1f Hz" % loom[peak], "GF spikes", gf[peak])
alpha = 0.02 / 3.0   # 3 s baseline
base = np.zeros(R.shape[1]); bases = []
for r in R:
    bases.append(base.copy()); base += alpha * (r - base)
bases = np.array(bases)
frames = [peak - 40, peak - 25, peak - 12, peak - 5, peak, peak + 15]
opts = {
  "gain 0.25": (0.25, lambda i: np.clip(R[i] / 30, 0, 2)),
  "gain 0.10": (0.10, lambda i: np.clip(R[i] / 30, 0, 2)),
  "gain 0.05": (0.05, lambda i: np.clip(R[i] / 30, 0, 2)),
  "gain 0.10, log rate": (0.10, lambda i: np.log1p(R[i] / 5)),
}
BV.WEIGHT_POW, BV.GLOW_GAIN, BV.WIRING_DIM = 0.7, 0.9, 0.10
bv = BV.BrainView(w.brain, pygame, scale=1.0)
tw, th = bv.base.get_size()
out = pygame.Surface(((tw + 6) * len(frames), (th + 20) * len(opts) + 20))
f = pygame.font.SysFont("consolas", 12)
for j, fr in enumerate(frames):
    out.blit(f.render(f"{(fr-peak)*20:+d} ms", True, (230, 230, 230)), (j * (tw + 6) + 4, 2))
for i, (name, (gain, fn)) in enumerate(opts.items()):
    y = 20 + i * (th + 20)
    out.blit(f.render(name, True, (230, 230, 230)), (4, y))
    for j, fr in enumerate(frames):
        act = fn(fr)
        img = np.stack([(F @ act).reshape(bv.H, bv.W) for F in bv.F], -1)
        glow = bv._surface(1 - np.exp(-gain * img))
        s = bv.base.copy(); s.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)
        out.blit(s, (j * (tw + 6), y + 16))
pygame.image.save(out, "data/glow_gain.png"); print("ok")
