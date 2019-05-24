import time
import pygame

from .gameobjects import World, Wall, Particle, Player, Ghost, Explosion
from .forgetlist import Forgetlist
from .geometry import Position, Line
from .util import randpos, randline
from .graphics import draw_world


_WIDTH = 1000
_HEIGHT = 600
SIZE = Position(_WIDTH, _HEIGHT)


def _quit():
    pygame.quit()
    exit(0)


def _input():
    evts = pygame.event.get()
    for evt in evts:
        if evt.type == pygame.QUIT:
            _quit()
        yield evt


def setup_game():
    player = Player(Position(SIZE.x // 2, SIZE.y // 2))
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


def _update_ghosts(world, now, timestep=1):
    ghosts = []
    for ghost in world.ghosts:
        ghosts += ghost.tick(world.size, now, timestep)
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


def _handle_mousebuttondown(world, evt, now):
    pos = evt.pos
    world.history.append(pos)
    radius = max(1, 20 - 5 * len(world.explosions))
    world.explosions.append(Explosion(pos=pos, start=now, ttl=1.0, radius=radius))
    return world


def _handle_mousemotion(world, evt, now):
    pos = evt.pos
    world.history.append(pos)
    player = world.player.but(pos=Position(*pos))
    return world.but(player=player)


def _handle_movement(world, key, now):
    if key == pygame.K_w:
        return world.but(player=world.player.up)
    if key == pygame.K_a:
        return world.but(player=world.player.left)
    if key == pygame.K_s:
        return world.but(player=world.player.down)
    if key == pygame.K_d:
        return world.but(player=world.player.right)
    return world


def _handle_keydown(world, evt, now):
    key = evt.key
    if key in (pygame.K_q, pygame.K_ESCAPE):
        _quit()

    return _handle_movement(world, key, now)


def _exit_if_done(world):
    numdead = sum([g.is_dead for g in world.ghosts])
    num = len(world.ghosts)
    if numdead == num:
        pygame.quit()
        quit("You won")
    if num - numdead > 100:
        pygame.quit()
        quit("You died")


def game_loop(surface):
    world = setup_game()
    prev = time.time()

    handlers = {
        pygame.MOUSEBUTTONDOWN: _handle_mousebuttondown,
        pygame.MOUSEMOTION: _handle_mousemotion,
        pygame.KEYDOWN: _handle_keydown,
    }
    while True:

        _exit_if_done(world)

        now = time.time()
        for evt in _input():  # flushing all events before drawing
            if evt.type in handlers:
                world = handlers[evt.type](world, evt, now)
        keys = pygame.key.get_pressed()
        for k in (pygame.K_w, pygame.K_d, pygame.K_a, pygame.K_s):
            if keys[k]:
                world = _handle_movement(world, k, now)

        world = world.but(ghosts=_update_ghosts(world, now, now - prev))

        draw_world(surface, world, speed=0, now=now)
        prev = now
        time.sleep(0.01)
