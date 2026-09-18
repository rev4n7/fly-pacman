import time, faulthandler; faulthandler.enable()
from flypac import game
import pygame
game.enable_dpi_awareness(); pygame.init()
from pygame._sdl2.video import Window, Renderer, Texture, WINDOWPOS_CENTERED
dw, dh = pygame.display.get_desktop_sizes()[0]
k = min(dw * 0.96 / 1920, dh * 0.86 / 1080, 1.0)
win = Window("test", size=(int(1920 * k), int(1080 * k)), resizable=True, position=WINDOWPOS_CENTERED)
ren = Renderer(win, accelerated=1, vsync=False)
ren.logical_size = (1920, 1080)
tex = Texture(ren, (1920, 1080), streaming=True)
import sys
fmt = sys.argv[1] if len(sys.argv) > 1 else "24"
canvas = {"24": pygame.Surface((1920, 1080)), "32": pygame.Surface((1920, 1080), 0, 32),
          "argb": pygame.Surface((1920, 1080), pygame.SRCALPHA, 32)}[fmt]
print("canvas bitsize", canvas.get_bitsize(), "masks", canvas.get_masks(), flush=True)
w = game.World(); r = game.Renderer(w, pygame, canvas)
def frames(n):
    t = time.time()
    for _ in range(n):
        for ev in pygame.event.get(): pass
        w.step(); r.draw(); tex.update(canvas); ren.clear(); tex.draw(); ren.present()
    return 1000 * (time.time() - t) / n
print("window", win.size, "desktop", (dw, dh), f"frame {frames(100):.1f} ms", flush=True)
win.set_fullscreen(desktop=True); print("fullscreen", win.size, f"{frames(40):.1f} ms", flush=True)
win.set_windowed(); win.size = (1200, 675); frames(10); print("windowed small", win.size, f"{frames(60):.1f} ms", flush=True)
t = time.time(); tex.update(canvas); print("texture upload ms", round(1000 * (time.time() - t), 2))
print("done")
