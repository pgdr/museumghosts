import math
import time
from collections import namedtuple
from dataclasses import dataclass
from .util import Position
from .util import intersects
from .forgetlist import Forgetlist
import pygame

ghost_size = Position(24, 24)
ghost_png = pygame.image.load("g1.png")
ghost_png = pygame.transform.scale(ghost_png, ghost_size.tup)

ghost_dead_png = pygame.image.load("g_dead.png")
ghost_dead_png = pygame.transform.scale(ghost_dead_png, ghost_size.tup)

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

    def direction(self):
        return (self.history[-1] - self.history[0]).tup

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


@dataclass(frozen=True)
class Wall:
    p1: Position
    p2: Position

    def draw(self, surface):
        pygame.draw.line(surface, (255, 255, 255), self.p1.tup, self.p2.tup, 2)


@dataclass(frozen=True)
class Particle:
    pos: Position

    def direcs(self, fov=TAU, rot=0.0):
        """Given field of view fov and rotation in radians yields actual fov.

        """
        assert 0 <= fov <= TAU, f"fov was not in [0,2pi]: {fov}"
        assert 0 <= rot <= TAU, f"rot was not in [0,2pi]: {rot}"
        rad = rot + math.pi  # rotate half way agains direction
        while fov >= 0:
            x = math.cos(rad)
            y = math.sin(rad)
            rad += 0.01
            rad %= TAU
            fov -= 0.01
            yield Position(x, y)

    def _get_fov_rot(self, speed, direction):
        fov = max(0.1, TAU - (speed / 100.0))
        rot = (TAU + math.atan2(direction[1], direction[0])) % TAU
        return fov, rot

    def draw(self, surface, world=None, speed=0, direction=(1, 0)):
        fov, rot = self._get_fov_rot(speed, direction)
        color = (255, 0, 0)
        walls = world.walls
        self._draw_walls(surface, walls, fov, rot)
        self._draw_ghosts(surface, world, fov=fov, rot=rot)
        pygame.draw.circle(surface, color, round(self.pos), 4)

    def _draw_walls(self, surface, walls, fov, rot):

        for direc in self.direcs(fov, rot):
            best = None
            dist = 2000
            for wall in walls:
                pos = intersects(wall, Wall(self.pos, self.pos + direc), ray=True)
                if not pos:
                    continue
                dist_ = self.pos.dist(pos)
                if dist_ < dist:
                    dist = dist_
                    best = pos

            if best is not None:
                pygame.draw.line(surface, (255, 255, 255), self.pos.tup, best.tup)

    def _draw_ghosts(self, surface, world, fov, rot):
        """Draw all ghosts within view."""
        pos = world.player
        walls = world.walls
        for ghost in world.ghosts:
            line = Wall(pos.pos, ghost.pos)
            for wall in walls:
                if intersects(line, wall, ray=False):
                    break
            else:
                # TODO check that line falls within fov
                surface.blit(ghost.sprite, (ghost.pos - ghost_size / 2).tup)


@dataclass(frozen=True)
class Ghost:
    particle: Particle
    is_dead: bool = False

    @property
    def pos(self):
        return self.particle.pos  # composition relay

    @property
    def sprite(self):
        return ghost_dead_png if self.is_dead else ghost_png

    def kill(self):
        return Ghost(self.particle, is_dead=True)


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
