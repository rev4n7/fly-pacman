import sys, faulthandler; faulthandler.enable()
from flypac import game
import pygame
game.enable_dpi_awareness(); pygame.init()
screen = game.make_window(pygame)
from pygame._sdl2.video import Window
win = Window.from_display_module()
print("desktop", pygame.display.get_desktop_sizes(), "window size", win.size, flush=True)
w = game.World(); r = game.Renderer(w, pygame, screen)
def frames(n):
    for _ in range(n):
        pygame.event.pump(); w.step(); r.draw(); pygame.display.flip()
frames(20); print("normal ok", flush=True)
pygame.display.toggle_fullscreen(); frames(30); print("fullscreen on ok", flush=True)
pygame.display.toggle_fullscreen(); frames(30); print("fullscreen off ok", flush=True)
win.size = (1000, 562); frames(30); print("resize ok", win.size, flush=True)
game_restart = game.World(ghost_speed=2.25); r.set_world(game_restart); w = game_restart; frames(20); print("restart ok", flush=True)
pygame.quit(); print("done", flush=True)
