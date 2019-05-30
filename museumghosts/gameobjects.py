import math
from dataclasses import dataclass, field
import time
import random

import pygame

from .graphics import draw_ghosts, draw_vision
from .geometry import Position, Line, intersects, crosses_wall
from .forgetlist import Forgetlist

GHOST_SIZE = Position(24, 24)
GHOST_PNG = pygame.image.load("g1.png")
GHOST_PNG = pygame.transform.scale(GHOST_PNG, GHOST_SIZE.tup)

GHOST_DEAD_PNG = pygame.image.load("g_dead.png")
GHOST_DEAD_PNG = pygame.transform.scale(GHOST_DEAD_PNG, GHOST_SIZE.tup)


GUARD_SIZE = Position(24, 24)
GUARD_PNG = pygame.image.load("guard.png")
GUARD_PNG = pygame.transform.scale(GUARD_PNG, GUARD_SIZE.tup)


TAU = 2 * math.pi


@dataclass(frozen=True)
class World:
    size: Position
    player: list
    ghosts: list
    walls: list
    explosions: Forgetlist
    history: Forgetlist

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
        for ghost in self.ghosts:
            if self._intersects_ghost(ray, ghost):
                return self.but(
                    ghosts=self.ghosts.remove(ghost),
                    explosions=self.explosions.append(Explosion(ray, now, 3)),
                )
        return self


@dataclass(frozen=True, eq=True)
class Wall:
    line: Line

    def draw(self, surface):
        p1, p2 = self.line
        pygame.draw.line(surface, (255, 255, 255), p1.tup, p2.tup, 5)


@dataclass(frozen=True)
class Particle:
    pos: Position


@dataclass(frozen=True)
class Player(Particle):

    direction: Position = Position(0, 0)
    vision: Position = Position(0, 0)

    def but(self, pos=None, direction=None, vision=None):
        pos = self.pos if pos is None else pos
        direction = self.direction if direction is None else direction
        vision = self.vision if vision is None else vision
        return Player(pos, direction, vision)

    def draw(self, surface, world, speed=0):
        color = (255, 0, 0)
        draw_vision(surface, world)
        draw_ghosts(surface, world)
        surface.blit(GUARD_PNG, (self.pos - GUARD_SIZE / 2).tup)

    def freeze(self):
        return self.but(direction=Position(0, 0))

    def _move(self, world, npos, direction):
        if crosses_wall(world, Line(self.pos, npos)):
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


@dataclass(frozen=True)
class Ghost:
    particle: Particle
    time: float = 0
    direction: Position = field(default_factory=_random_direction)
    is_dead: bool = False

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
        width, height = size.x, size.y
        dist = self.direction * elapsed
        partic = self.particle
        if self.is_dead:
            return [self.but(particle=partic)]

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


@dataclass(frozen=True)
class Explosion:
    ray: Line
    start: float
    ttl: float

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
