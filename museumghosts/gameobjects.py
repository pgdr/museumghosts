import math

from dataclasses import dataclass
from .util import Position
from .util import intersects
import pygame


TAU = 2 * math.pi


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

    def draw(
        self, surface, walls=tuple(), color=(255, 0, 0), speed=0, direction=(1, 0)
    ):
        self._draw_walls(surface, walls, speed=speed, direction=direction)
        pygame.draw.circle(surface, color, round(self.pos), 4)

    def _draw_walls(self, surface, walls, speed, direction):
        fov = max(0.1, TAU - (speed / 100.0))
        rot = (TAU + math.atan2(direction[1], direction[0])) % TAU  # radians

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
