import math
import sys
import random
import pygame

from .gameobjects import *

ghost_png = pygame.image.load("ghost.png")
ghost_png = pygame.transform.scale(ghost_png, (24, 24))


from noise import pnoise1

from collections import namedtuple


World = namedtuple("World", "particle ghosts walls")

from .forgetlist import Forgetlist
from .util import Position
from .util import intersects

WIDTH = 1000
HEIGHT = 600


def draw_ghosts(surface, world):
    """Draw all ghosts within view."""
    pos = world.particle
    walls = world.walls

    for ghost in world.ghosts:
        line = Wall(pos.pos, ghost.pos)
        for wall in walls:
            if intersects(line, wall, ray=False):
                break
        else:
            surface.blit(ghost_png, ghost.pos.tup)


def _input(events):
    for event in events:
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            sys.exit(0)
        else:
            return event


def draw_world(surface, world, speed, direction):
    particle = world.particle
    ghosts = world.ghosts
    walls = world.walls

    surface.fill((0, 0, 0))

    for wall in walls:
        wall.draw(surface)

    particle.draw(surface, walls=walls, speed=speed, direction=direction)
    draw_ghosts(surface, world)

    pygame.display.flip()


def rand(max_=None):
    if max_ is None:
        max_ = min(WIDTH, HEIGHT)
    return random.randint(0, max_)


def randpos():
    return Position(rand(WIDTH), rand(HEIGHT))


def randline():
    return randpos(), randpos()


def total_dist_travelled(hist):
    lst = [x for x in hist]
    if len(lst) < 2:
        return 0
    return sum(lst[i].dist(lst[i + 1]) for i in range(len(lst) - 1))


def average_speed(hist):
    return total_dist_travelled(hist) / hist.duration


def game_loop(surface):
    particle = Particle(Position(100, 100))
    ghosts = [Particle(Position(200, 200))]

    bnw = Position(0, 0)
    bne = Position(WIDTH, 0)
    bsw = Position(0, HEIGHT)
    bse = Position(WIDTH, HEIGHT)

    boundary = [Wall(bnw, bne), Wall(bne, bse), Wall(bse, bsw), Wall(bsw, bnw)]

    world = World(particle, ghosts, boundary + [Wall(*randline()) for _ in range(10)])

    xoff = 10.0
    yoff = 100.0

    walls = world.walls
    history = Forgetlist(3.0)  # remember last half second of events
    while True:
        evt = _input(pygame.event.get())
        pos = Position(WIDTH * pnoise1(xoff) // 100, HEIGHT * pnoise1(yoff) // 100)

        xoff += 10.01
        yoff += 20.01
        ghosts = [Particle(ghosts[0].pos + pos)]
        speed = 0
        direction = (1, 0)
        if evt is not None and evt.type == pygame.MOUSEMOTION:
            pos = Position(*evt.pos)
            particle = Particle(Position(*pos))
            history.append(pos)
        speed = average_speed(history)
        try:
            direction = (history[-1] - history[0]).tup
        except IndexError:
            pass

        world = World(particle, ghosts, walls)
        if particle.pos.dist(ghosts[0].pos) <= 10:
            print("You won")
            exit("0")
        draw_world(surface, world, speed, direction=direction)


def main():
    width, height = WIDTH, HEIGHT

    pygame.init()
    pygame.display.set_mode((width, height))
    screen = pygame.display.get_surface()

    game_loop(screen)


if __name__ == "__main__":
    main()
