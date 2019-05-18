import math
from collections import namedtuple
import pygame

from .gameobjects import *
from .forgetlist import Forgetlist
from .util import Position
from .util import intersects
from .util import perlin, randpos, randline
from .graphics import draw_world

World = namedtuple("World", "size player ghosts walls explosions")


def _with(world, size=None, player=None, ghosts=None, walls=None, explosions=None):
    return World(
        size or world.size,
        player or world.player,
        ghosts or world.ghosts,
        walls or world.walls,
        explosions or world.explosions,
    )


_WIDTH = 1000
_HEIGHT = 600
SIZE = Position(_WIDTH, _HEIGHT)


def _input(events):
    for event in events:
        if event.type in (pygame.QUIT, pygame.KEYDOWN):
            exit(0)
        else:
            return event


def total_dist_travelled(hist):
    lst = [x for x in hist]
    if len(lst) < 2:
        return 0
    return sum(lst[i].dist(lst[i + 1]) for i in range(len(lst) - 1))


def average_speed(hist):
    return total_dist_travelled(hist) / hist.duration


def setup_game():
    player = Particle(Position(SIZE.x // 2, SIZE.y // 2))
    ghosts = [
        Ghost(Particle(randpos(SIZE))),
        Ghost(Particle(randpos(SIZE))),
        Ghost(Particle(randpos(SIZE))),
        Ghost(Particle(randpos(SIZE))),
    ]

    bnw = Position(0, 0)
    bne = Position(SIZE.x, 0)
    bsw = Position(0, SIZE.y)
    bse = Position(SIZE.x, SIZE.y)

    boundary = [Wall(bnw, bne), Wall(bne, bse), Wall(bse, bsw), Wall(bsw, bnw)]

    world = World(
        SIZE,
        player,
        ghosts,
        boundary + [Wall(*randline(SIZE)) for _ in range(10)],
        Forgetlist(1.5),  # max ttl for explosions
    )
    return world


def _update_ghosts(world, now):
    ghosts = [
        Ghost(
            Particle((ghost.pos + perlin(world.size, *ghost.pos.tup)).normalize(world)),
            is_dead=ghost.is_dead,
        )
        if not ghost.is_dead
        else Ghost(ghost.particle, is_dead=ghost.is_dead)
        for ghost in world.ghosts
    ]
    dead = []
    for idx, ghost in enumerate(ghosts):
        for explosion in world.explosions:
            if (
                explosion.alive(now)
                and ghost.pos.dist(explosion.pos) <= explosion.radius
            ):
                dead.append(idx)
    for idx in dead:
        ghosts[idx] = ghosts[idx].kill()
    return ghosts


def _handle_mousebuttondown(world, pos, now):
    radius = max(1, 20 - 5 * len(world.explosions))
    world.explosions.append(Explosion(pos=pos, start=now, ttl=1.0, radius=radius))
    return world


def _handle_mousemotion(world, pos, now):
    player = Particle(Position(*pos))
    return _with(world, player=player)


def game_loop(surface):
    world = setup_game()
    walls = world.walls
    history = Forgetlist(3.0)  # remember last half second of events
    while True:
        now = time.time()
        evt = _input(pygame.event.get())
        player = world.player
        speed = 0
        direction = (1, 0)
        if evt is not None:
            try:
                pos = Position(*evt.pos)
            except:
                print(f"unknown event {evt.type}")
            if evt.type == pygame.MOUSEBUTTONDOWN:
                world = _handle_mousebuttondown(world, pos, now)
            elif evt.type == pygame.MOUSEMOTION:
                world = _handle_mousemotion(world, pos, now)
            history.append(pos)

        world = _with(world, ghosts=_update_ghosts(world, now))
        speed = average_speed(history)
        try:
            direction = (history[-1] - history[0]).tup
        except IndexError:
            pass

        if all([g.is_dead for g in world.ghosts]):
            exit("You won")

        draw_world(surface, world, speed, direction=direction)
