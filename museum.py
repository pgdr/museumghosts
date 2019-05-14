import math
import sys
import random
import pygame
from noise import pnoise1

from dataclasses import dataclass
from collections import namedtuple

World = namedtuple("World", "particle walls")

WIDTH = 1000
HEIGHT = 600


@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other: "Position") -> "Position":
        return Position(self.x + other.x, self.y + other.y)

    def __iter__(self):
        yield self.x
        yield self.y

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (255, 255, 255), self.x, self.y, 1, 1)

    def dist(self, other: "Position") -> float:
        xs = (self.x - other.x) ** 2
        ys = (self.y - other.y) ** 2
        return math.sqrt(xs + ys)

    @property
    def tup(self):
        return (self.x, self.y)

    def normalize(self):
        return Position(min(max(0, self.x), WIDTH), min(max(0, self.y), HEIGHT))

    def __round__(self):
        return int(self.x), int(self.y)


@dataclass(frozen=True)
class Wall:
    p1: Position
    p2: Position

    def draw(self, surface):
        pygame.draw.line(surface, (255, 255, 255), self.p1.tup, self.p2.tup, 2)


@dataclass(frozen=True)
class Particle:
    pos: Position

    def direcs(self):
        for deg in range(0, 314 * 2):
            x = 10 * math.cos(deg / 100)
            y = 10 * math.sin(deg / 100)
            yield Position(x, y)

    def draw(self, surface, walls):
        self._draw_walls(surface, walls)
        pygame.draw.circle(surface, (255, 0, 0), round(self.pos), 4)

    def _draw_walls(self, surface, walls):
        for direc in self.direcs():
            best = None
            dist = 2000
            for wall in walls:
                pos = self.intersect(direc, wall)
                if not pos:
                    continue
                dist_ = self.pos.dist(pos)
                if dist_ < dist:
                    dist = dist_
                    best = pos

            if best is not None:
                pygame.draw.line(surface, (255, 255, 255), self.pos.tup, best.tup)

    def intersect(self, direc, wall):
        x1, y1 = wall.p1
        x2, y2 = wall.p2
        x3, y3 = self.pos
        x4, y4 = self.pos + direc

        t_n = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        if t_n == 0:
            return

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / t_n
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / t_n

        if 0 <= t <= 1 and u > 0:
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            return Position(x, y)


def _input(events):
    for event in events:
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            sys.exit(0)
        else:
            return event


def draw_world(surface, world):
    particle = world.particle
    walls = world.walls

    surface.fill((0, 0, 0))

    for wall in walls:
        wall.draw(surface)

    particle.draw(surface, walls)

    pygame.display.flip()


def rand(max_=None):
    if max_ is None:
        max_ = min(WIDTH, HEIGHT)
    return random.randint(0, max_)


def randpos():
    return Position(rand(WIDTH), rand(HEIGHT))


def randline():
    return randpos(), randpos()


def game_loop(surface):
    world = World(Particle(Position(100, 100)), [Wall(*randline()) for _ in range(10)])

    xoff = 0.0
    yoff = 10000.0

    walls = world.walls
    while True:
        evt = _input(pygame.event.get())
        if evt is None or evt.type != pygame.MOUSEMOTION:
            pos = world.particle.pos + Position(
                WIDTH * pnoise1(xoff) // 50, HEIGHT * pnoise1(yoff) // 50
            )
            xoff += 0.01
            yoff += 0.01
            pygame.time.wait(5)
        else:
            pos = Position(*evt.pos)
        pos = pos.normalize()
        world = World(Particle(Position(*pos)), walls)
        draw_world(surface, world)


def main():
    width, height = WIDTH, HEIGHT

    pygame.init()
    pygame.display.set_mode((width, height))
    screen = pygame.display.get_surface()

    game_loop(screen)


if __name__ == "__main__":
    main()
