import math
import random
import pygame

from .sprites import guard as guard_img
from .sprites import ghost as ghost_img
from .sprites import ghost_dead as ghost_dead_img

from .graphics import draw_ghosts, draw_vision
from .geometry import Position, Line, intersects, crosses_wall


GHOST_SIZE = Position(24, 24)
GHOST_PNG = ghost_img
GHOST_PNG = pygame.transform.scale(GHOST_PNG, GHOST_SIZE.tup)

GHOST_DEAD_PNG = ghost_dead_img
GHOST_DEAD_PNG = pygame.transform.scale(GHOST_DEAD_PNG, GHOST_SIZE.tup)


GUARD_SIZE = Position(24, 24)
GUARD_PNG = guard_img
GUARD_PNG = pygame.transform.scale(GUARD_PNG, GUARD_SIZE.tup)


TAU = 2 * math.pi


class World:
    def __init__(self, size, player, ghosts, walls, explosions, history):
        self.size = size
        self.player = player
        self.ghosts = ghosts
        self.walls = walls
        self.explosions = explosions
        self.history = history

    def but(
        self,
        size=None,
        player=None,
        ghosts=None,
        walls=None,
        explosions=None,
        history=None,
    ):
        return World(
            size or self.size,
            player or self.player,
            ghosts or self.ghosts,
            walls or self.walls,
            explosions or self.explosions,
            history or self.history,
        )

    @staticmethod
    def _intersects_ghost(ray, ghost):
        rad = 24
        x1 = ghost.pos.x + rad
        y1 = ghost.pos.y + rad
        x2 = ghost.pos.x - rad
        y2 = ghost.pos.y - rad
        if intersects(ray, Line(Position(x1, y1), Position(x2, y2)), ray=False):
            return True

    def fire(self, now):
        player = self.player
        ray = Line(player.pos, player.vision)
        for idx in range(len(self.ghosts)):
            ghost = self.ghosts[idx]
            if ghost.is_dead:
                continue
            if self._intersects_ghost(ray, ghost):
                nghosts = self.ghosts[:idx] + [ghost.kill()] + self.ghosts[idx + 1 :]

                return self.but(
                    ghosts=nghosts,
                    explosions=self.explosions.append(Explosion(ray, now, 3)),
                )
        return self


class Wall:
    def __init__(self, line):
        self.line = line

    def __eq__(self, other):
        if not isinstance(other, Wall):
            return NotImplemented
        return self.line == other.line

    def __hash__(self):
        return hash(self.line)

    def draw(self, surface):
        p1, p2 = self.line
        pygame.draw.line(surface, (255, 255, 255), p1.tup, p2.tup, 5)


class Particle:
    def __init__(self, pos):
        self.pos = pos

    def __eq__(self, other):
        if not isinstance(other, Particle):
            return NotImplemented
        return self.pos == other.pos

    def __hash__(self):
        return hash(self.pos)

    def __repr__(self):
        return "Particle({})".format(self.pos)


class Player(Particle):
    def __init__(self, pos, direction=Position(0, 0), vision=Position(0, 0)):
        super(Player, self).__init__(pos)
        self.direction = direction
        self.vision = vision

    def but(self, pos=None, direction=None, vision=None):
        pos = self.pos if pos is None else pos
        direction = self.direction if direction is None else direction
        vision = self.vision if vision is None else vision
        return Player(pos, direction, vision)

    def draw(self, surface, world):
        draw_vision(surface, world)
        draw_ghosts(surface, world)
        surface.blit(GUARD_PNG, (self.pos - GUARD_SIZE / 2).tup)

    def freeze(self):
        return self.but(direction=Position(0, 0))

    def _move(self, world, npos, direction):
        if crosses_wall(world.walls, Line(self.pos, npos)):
            return self.freeze().but(pos=self.pos).inside(world)
        return self.but(pos=npos, direction=direction).inside(world)

    def up(self, world):
        y = min(self.direction.y - 2, -1)
        npos = self.pos + Position(0, y)
        return self._move(world, npos, self.direction.but(y=y))

    def down(self, world):
        y = max(self.direction.y + 2, 1)
        npos = self.pos + Position(0, y)
        return self._move(world, npos, self.direction.but(y=y))

    def left(self, world):
        x = min(-1, self.direction.x - 2)
        npos = self.pos + Position(x, 0)
        return self._move(world, npos, self.direction.but(x=x))

    def right(self, world):
        x = max(1, self.direction.x + 2)
        npos = self.pos + Position(x, 0)
        return self._move(world, npos, self.direction.but(x=x))

    def inside(self, world):
        pad = 5  # hardcoded wall width
        x = min(max(pad, self.pos.x), world.size.x - pad)
        y = min(max(pad, self.pos.y), world.size.y - pad)
        pos = Position(x, y)
        if pos == self.pos:
            return self
        return self.freeze().but(pos=Position(x, y))


def _random_direction():
    # speed of ghost is (-0.2, 0.2)
    return Position(1 - 2 * random.random(), 1 - 2 * random.random()) / 5


class Ghost:
    def __init__(self, particle, time=0.0, direction=None, is_dead=False):
        self.particle = particle
        self.time = time
        self.direction = _random_direction() if direction is None else direction
        self.is_dead = is_dead

    def but(self, particle=None, time=None, direction=None, is_dead=None):
        return Ghost(
            particle if particle is not None else self.particle,
            time if time is not None else self.time,
            direction if direction is not None else self.direction,
            is_dead if is_dead is not None else self.is_dead,
        )

    @property
    def pos(self):
        return self.particle.pos  # composition relay

    @property
    def sprite(self):
        return GHOST_DEAD_PNG if self.is_dead else GHOST_PNG

    @property
    def size(self):
        return GHOST_SIZE

    def kill(self):
        return self.but(is_dead=True)

    def tick(self, size, now, elapsed):
        """Surprisingly returns a list of ghosts to replace this.
        """
        width, height = size.x, size.y
        dist = self.direction * elapsed
        partic = self.particle
        if self.is_dead:
            return [self]

        npos = self.pos + dist
        direction = self.direction
        if npos.x < 24:
            npos = Position(25, npos.y)
            direction = self.direction.flip_hor()
        if npos.x > width - 24:
            npos = Position(width - 25, npos.y)
            direction = self.direction.flip_hor()
        if npos.y < 24:
            npos = Position(npos.x, 25)
            direction = self.direction.flip_vert()
        if npos.y > height - 24:
            npos = Position(npos.x, height - 25)
            direction = self.direction.flip_vert()

        partic = Particle(npos)
        if now - self.time > 12:
            # spawn new ghosts
            return [
                self.but(particle=partic, time=now),
                self.but(
                    particle=Particle(partic.pos + Position(24, 24)),
                    direction=self.direction.flip_hor(),
                    time=now,
                ),
                self.but(
                    particle=Particle(partic.pos - Position(24, 24)),
                    direction=self.direction.flip_vert(),
                    time=now,
                ),
            ]
        return [self.but(particle=partic, direction=direction)]


class Explosion:
    def __init__(self, ray, start, ttl):
        self.ray = ray
        self.start = start
        self.ttl = ttl

    def draw(self, surface, now):
        if not self.alive(now):
            return
        done = max(1, 255 * (self.ttl - self.age(now)))
        red = done / self.ttl
        brightness = (2.2 ** math.log(done)) / self.ttl
        col = (red, brightness, 0)
        pygame.draw.line(surface, col, round(self.ray.p1), round(self.ray.p2), 3)

    def age(self, now):
        return now - self.start

    def alive(self, now):
        return self.age(now) < self.ttl

    def destroyed(self, now):
        return not self.alive(now)
