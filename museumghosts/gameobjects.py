import math
from dataclasses import dataclass

import pygame

from .graphics import draw_ghosts, draw_vision
from .geometry import Position, Line
from .util import perlin
from .forgetlist import Forgetlist

GHOST_SIZE = Position(24, 24)
GHOST_PNG = pygame.image.load("g1.png")
GHOST_PNG = pygame.transform.scale(GHOST_PNG, GHOST_SIZE.tup)

GHOST_DEAD_PNG = pygame.image.load("g_dead.png")
GHOST_DEAD_PNG = pygame.transform.scale(GHOST_DEAD_PNG, GHOST_SIZE.tup)

TAU = 2 * math.pi


@dataclass(frozen=True)
class World:
    size: Position
    player: list
    ghosts: list
    walls: list
    explosions: Forgetlist
    history: Forgetlist

    def total_dist_travelled(self):
        hist = self.history
        lst = [x for x in hist]
        if len(lst) < 2:
            return 0
        return sum(lst[i].dist(lst[i + 1]) for i in range(len(lst) - 1))

    def average_speed(self):
        hist = self.history
        return self.total_dist_travelled() / hist.duration

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


@dataclass(frozen=True, eq=True)
class Wall:
    line: Line

    def draw(self, surface):
        p1, p2 = self.line
        pygame.draw.line(surface, (100, 200, 50), p1.tup, p2.tup, 7)


@dataclass(frozen=True)
class Particle:
    pos: Position

    def draw(self, surface, world, speed=0):
        color = (255, 0, 0)
        draw_vision(surface, world)
        draw_ghosts(surface, world)
        pygame.draw.circle(surface, color, round(self.pos), 4)


@dataclass(frozen=True)
class Ghost:
    particle: Particle
    is_dead: bool = False

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
        return Ghost(self.particle, is_dead=True)

    def perlin_move(self, size):
        partic = self.particle
        if not self.is_dead:
            npos = self.pos + perlin(size, *self.pos.tup)
            partic = Particle(npos.normalize(size, padding=24))
        return Ghost(partic, is_dead=self.is_dead)


@dataclass(frozen=True)
class Explosion:
    pos: Position
    start: float
    ttl: float
    radius: float

    def draw(self, surface, now):
        if not self.alive(now):
            return
        done = max(1, 255 * (self.ttl - self.age(now)))
        red = done / self.ttl
        brightness = (2.2 ** math.log(done)) / self.ttl
        col = (red, brightness, 0)
        pygame.draw.circle(surface, col, round(self.pos), self.radius)

    def age(self, now):
        return now - self.start

    def alive(self, now):
        return self.age(now) < self.ttl

    def destroyed(self, now):
        return not self.alive(now)
