import math
import sys
import random
from collections import namedtuple
import pygame
from noise import pnoise1

from .gameobjects import *
from .forgetlist import Forgetlist
from .util import Position
from .util import intersects


World = namedtuple("World", "particle ghosts walls explosions")


WIDTH = 1000
HEIGHT = 600
_PERLINX = 10.0
_PERLINY = 2000.0


def perlin(x, y):
    global WIDTH, HEIGTH, _PERLINX, _PERLINY
    x = WIDTH * pnoise1(_PERLINX + x) // 100
    y = HEIGHT * pnoise1(_PERLINY + y) // 100
    _PERLINX += 1.01
    _PERLINY += 0.01
    pos = Position(x, y)
    return pos


def _input(events):
    for event in events:
        if event.type in (pygame.QUIT, pygame.KEYDOWN):
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

    particle.draw(surface, world=world, speed=speed, direction=direction)
    for explosion in world.explosions:
        explosion.draw(surface, time.time())

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
    particle = Particle(Position(WIDTH // 2, HEIGHT // 2))
    ghosts = [
        Particle(randpos()),
        Particle(randpos()),
        Particle(randpos()),
        Particle(randpos()),
    ]

    bnw = Position(0, 0)
    bne = Position(WIDTH, 0)
    bsw = Position(0, HEIGHT)
    bse = Position(WIDTH, HEIGHT)

    boundary = [Wall(bnw, bne), Wall(bne, bse), Wall(bse, bsw), Wall(bsw, bnw)]

    world = World(
        particle,
        ghosts,
        boundary + [Wall(*randline()) for _ in range(10)],
        Forgetlist(10.0),
    )

    walls = world.walls
    history = Forgetlist(3.0)  # remember last half second of events
    while True:
        now = time.time()
        evt = _input(pygame.event.get())

        ghosts = [
            Particle(ghost.pos + perlin(*ghost.pos.tup)) for ghost in world.ghosts
        ]
        speed = 0
        direction = (1, 0)
        if evt is not None and evt.type == pygame.MOUSEMOTION:
            pos = Position(*evt.pos)
            particle = Particle(Position(*pos))
            history.append(pos)
        if evt is not None and evt.type == pygame.MOUSEBUTTONDOWN:
            world.explosions.append(Explosion(pos=pos, start=now, ttl=1.0, radius=20))
        speed = average_speed(history)
        try:
            direction = (history[-1] - history[0]).tup
        except IndexError:
            pass

        world = World(particle, ghosts, walls, world.explosions)

        to_del = []
        for ghost in world.ghosts:
            for explosion in world.explosions:
                if (
                    explosion.alive(now)
                    and ghost.pos.dist(explosion.pos) <= explosion.radius
                ):
                    print(f"exploded {ghost}")
                    to_del.append(ghost)
        for ghost in to_del:
            world.ghosts.remove(ghost)

        if not world.ghosts:
            exit("You won")

        draw_world(surface, world, speed, direction=direction)


def main():
    width, height = WIDTH, HEIGHT

    pygame.init()
    pygame.display.set_mode((width, height))
    screen = pygame.display.get_surface()

    game_loop(screen)


if __name__ == "__main__":
    main()
