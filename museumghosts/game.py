import time
import pygame

from .gameobjects import World, Wall, Particle, Ghost, Explosion
from .forgetlist import Forgetlist
from .geometry import Position, Line
from .util import randpos, randline
from .graphics import draw_world


_WIDTH = 1000
_HEIGHT = 600
SIZE = Position(_WIDTH, _HEIGHT)


def _input():
    evts = pygame.event.get()
    for evt in evts:
        if evt.type in (pygame.QUIT, pygame.KEYDOWN):
            exit(0)
        yield evt


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

    boundary = [
        Wall(Line(bnw, bne)),
        Wall(Line(bne, bse)),
        Wall(Line(bse, bsw)),
        Wall(Line(bsw, bnw)),
    ]

    world = World(
        SIZE,
        player,
        ghosts,
        boundary + [Wall(randline(SIZE)) for _ in range(10)],
        Forgetlist(1.5),  # max ttl for explosions
        Forgetlist(3.0),  # remember last three seconds of events
    )
    return world


def _update_ghosts(world, now):
    ghosts = [ghost.perlin_move(world.size) for ghost in world.ghosts]
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


def _exit_if_done(world):
    if all([g.is_dead for g in world.ghosts]):
        exit("You won")


def game_loop(surface):
    world = setup_game()

    handlers = {
        pygame.MOUSEBUTTONDOWN: _handle_mousebuttondown,
        pygame.MOUSEMOTION: _handle_mousemotion,
    }
    while True:
        _exit_if_done(world)
        for evt in _input():  # flushing all events before drawing
            now = time.time()
            if evt.type in handlers:
                pos = Position(*evt.pos)
                world.history.append(pos)

                world = handlers[evt.type](world, pos, now)

        world = world.but(ghosts=_update_ghosts(world, now))
        speed = world.average_speed()

        draw_world(surface, world, speed, now=now)
