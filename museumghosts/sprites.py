import os
import pygame


def _img(fname):
    return os.path.join(os.path.dirname(__file__), "assets", fname)


def _load(fname):
    return pygame.image.load(_img(fname))


floor = _load("floor.png")
guard = _load("guard.png")
ghost = _load("g1.png")
ghost_dead = _load("g_dead.png")
