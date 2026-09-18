import sys, time, numpy as np, flypac.brain as B
for ab in [float(x) for x in sys.argv[1:]]:
    B.ADAPT_B = ab
    b = B.Brain(seed=2); o = b.out; gf = [o["DNp01_L"], o["DNp01_R"]]
    b.input_rate[:] = 0; b.input_rate[b.loom] = 150; t = time.time(); c1 = b.step(0.3); el = time.time() - t
    b.sense(); c2 = b.step(0.3); c3 = b.step(0.5)
    print(f"adapt={ab}: N={b.N} 0.3s sim {el:.2f}s | strong on GF {c1[gf].tolist()} | off 0-.3 {c2.sum()} | off .3-.8 {c3.sum()} GF {c3[gf].tolist()}")
    for rate in [10, 30]:
        row = []
        for bearing in [0, -90, 180]:
            b.reset(); ov = b._rf_overlap(b.loom, bearing, 40.0)
            b.input_rate[:] = 0; b.input_rate[b.loom] = rate * ov / ov.max()
            c = b.step(0.3); s = lambda k: c[o[k + "_L"]] + c[o[k + "_R"]]
            side = lambda sd: sum(c[o[k + "_" + sd]] for k in ["DNp01", "DNp02", "DNp04", "DNp11"])
            row.append(f"b={bearing:4d}: GF {c[o['DNp01_L']]:3d}/{c[o['DNp01_R']]:3d} p02 {s('DNp02'):3d} p11 {s('DNp11'):3d} L|R {side('L'):3d}|{side('R'):3d}")
        print(f"   {rate:2d}Hz  " + " || ".join(row))
