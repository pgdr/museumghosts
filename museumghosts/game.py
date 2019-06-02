import pygame

from .gameobjects import World, Wall, Particle, Player, Ghost, Explosion
from .forgetlist import Forgetlist
from .geometry import Position, Line
from .util import randpos, randline
from .graphics import draw_world

from .mazegen import random_maze


_WIDTH = 1100
_HEIGHT = 700
SIZE = Position(_WIDTH, _HEIGHT)


def merge(e1, e2):
    p11, p12 = e1
    p21, p22 = e2
    x11, y11 = p11
    x12, y12 = p12
    x21, y21 = p21
    x22, y22 = p22
    # horizontal
    if y11 == y12 == y21 == y22 and x11 == x21:
        return Line(Position(x12, y11), Position(x22, y11))
    if y11 == y12 == y21 == y22 and x11 == x22:
        return Line(Position(x12, y11), Position(x21, y11))
    if y11 == y12 == y21 == y22 and x12 == x21:
        return Line(Position(x11, y11), Position(x22, y11))
    if y11 == y12 == y21 == y22 and x12 == x22:
        return Line(Position(x11, y11), Position(x21, y11))
    # vertical
    if x11 == x12 == x21 == x22 and y11 == y21:
        return Line(Position(x11, y12), Position(x11, y22))
    if x11 == x12 == x21 == x22 and y11 == y22:
        return Line(Position(x11, y12), Position(x11, y21))
    if x11 == x12 == x21 == x22 and y12 == y21:
        return Line(Position(x11, y11), Position(x11, y22))
    if x11 == x12 == x21 == x22 and y12 == y22:
        return Line(Position(x11, y11), Position(x11, y21))


def maze():
    scal = 200
    M = random_maze(*(SIZE // scal).tup)

    edges = set(M.edges)
    edited = True
    while edited:
        edited = False
        delete = set()
        add = set()
        for e1 in edges:
            if edited:
                break
            for e2 in edges:
                if e1 == e2:
                    continue
                m = merge(e1, e2)
                if m:
                    delete.add(e1)
                    delete.add(e2)
                    add.add(m)
                    edited = True
                    break
        edges = (edges - delete) | add

    for p1, p2 in M.edges:
        line = Line(
            Position(*p1) * scal + Position(100, 100),
            Position(*p2) * scal + Position(100, 100),
        )
        yield Wall(line)


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
        boundary + list(maze()),
        Forgetlist(1.5),  # max ttl for explosions
        Forgetlist(3.0),  # remember last three seconds of events
    )
    return world


def _update_ghosts(world, now, elapsed=50):
    ghosts = []

    for ghost in world.ghosts:
        ghosts += ghost.tick(world.size, now, elapsed)

    return ghosts


def _handle_mousebuttondown(world, evt, now):
    return world.fire(now)


def _handle_mousemotion(world, evt, now):
    pos = evt.pos
    player = world.player.but(vision=Position(*pos))
    return world.but(player=player)


def _handle_movement(world, key, now):
    if key == pygame.K_w:
        return world.but(player=world.player.up(world))
    if key == pygame.K_a:
        return world.but(player=world.player.left(world))
    if key == pygame.K_s:
        return world.but(player=world.player.down(world))
    if key == pygame.K_d:
        return world.but(player=world.player.right(world))
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


def collision_detection(world):
    player = world.player
    for ghost in world.ghosts:
        if not ghost.is_dead and player.pos.dist(ghost.pos) <= max(ghost.size):
            exit("collision dead")


def game_loop(surface):
    world = setup_game()
    clock = pygame.time.Clock()

    handlers = {
        pygame.MOUSEBUTTONDOWN: _handle_mousebuttondown,
        pygame.MOUSEMOTION: _handle_mousemotion,
        pygame.KEYDOWN: _handle_keydown,
    }
    while True:
        collision_detection(world)
        _exit_if_done(world)

        now = pygame.time.get_ticks() / 1000.0  # milliseconds since init
        elapsed = clock.get_time()

        for evt in _input():  # flushing all events before drawing
            if evt.type in handlers:
                world = handlers[evt.type](world, evt, now)
        keys = pygame.key.get_pressed()
        moved = False
        for k in (pygame.K_w, pygame.K_d, pygame.K_a, pygame.K_s):
            if keys[k]:
                world = _handle_movement(world, k, now)
                moved = True
        if not moved:
            world = world.but(player=world.player.freeze())

        world = world.but(player=world.player)

        world = world.but(ghosts=_update_ghosts(world, now, elapsed))

        draw_world(surface, world, now=now)
        clock.tick(50)
