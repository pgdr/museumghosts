import math
import pygame

from .gameobjects import *
from .forgetlist import Forgetlist
from .util import Position
from .util import intersects
from .util import perlin, randpos, randline
from .graphics import draw_world


_WIDTH = 1000
_HEIGHT = 600
SIZE = Position(_WIDTH, _HEIGHT)


def _input(events):
    for event in events:
        if event.type in (pygame.QUIT, pygame.KEYDOWN):
            exit(0)
        else:
            return event


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
        Forgetlist(3.0),  # remember last three seconds of events
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
    return world.but(player=player)


def game_loop(surface):
    world = setup_game()
    walls = world.walls
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
            world.history.append(pos)

        world = world.but(ghosts=_update_ghosts(world, now))
        speed = world.average_speed()
        try:
            direction = world.direction()
        except IndexError:
            pass

        if all([g.is_dead for g in world.ghosts]):
            exit("You won")

        draw_world(surface, world, speed, direction=direction)
