import os; os.environ["SDL_VIDEODRIVER"] = "dummy"
import numpy as np, pygame, flypac.brainview as BV
from flypac.world import World
pygame.init(); screen = pygame.display.set_mode((10, 10))
w = World(seed=0)
states = {}
while w.stats.time < 40 and len(states) < 2:
    w.step()
    if w.stats.time > 6 and "calm" not in states and not w.motor["jump"]:
        states["calm"] = (w.brain.rates.copy(), w.counts.copy())
    if w.stats.jumps >= 2 and "jump" not in states:
        for _ in range(2): w.step()
        states["jump"] = (w.brain.rates.copy(), w.counts.copy())
opts = [dict(WEIGHT_POW=0.5, RATE_REF=30, GLOW_GAIN=0.9, WIRING_DIM=0.16),
        dict(WEIGHT_POW=1.0, RATE_REF=60, GLOW_GAIN=0.6, WIRING_DIM=0.10),
        dict(WEIGHT_POW=1.0, RATE_REF=100, GLOW_GAIN=0.5, WIRING_DIM=0.10),
        dict(WEIGHT_POW=1.5, RATE_REF=80, GLOW_GAIN=0.8, WIRING_DIM=0.08)]
tiles = []
for o in opts:
    for k, v in o.items(): setattr(BV, k, v)
    bv = BV.BrainView(w.brain, pygame, scale=1.4)
    row = []
    for name in ["calm", "jump"]:
        rates, counts = states[name]
        w.brain.rates = rates
        bv.update(counts, w)
        surf = bv.base.copy(); surf.blit(bv.bloom, (0, 0), special_flags=pygame.BLEND_ADD); surf.blit(bv.glow, (0, 0), special_flags=pygame.BLEND_ADD)
        row.append(surf)
    tiles.append((o, row))
tw, th = tiles[0][1][0].get_size()
out = pygame.Surface((tw * 2 + 10, (th + 22) * len(tiles)))
f = pygame.font.SysFont("consolas", 13)
for i, (o, row) in enumerate(tiles):
    y = i * (th + 22)
    out.blit(f.render(f"option {i+1}: {o}   (left calm | right just after GF takeoff)", True, (230, 230, 230)), (4, y + 3))
    for j, sf in enumerate(row): out.blit(sf, (j * (tw + 10), y + 20))
pygame.image.save(out, "data/glow_options.png"); print("ok")
