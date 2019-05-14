import math
import sys
from time import sleep
import random
import pygame
from noise import pnoise2

from dataclasses import dataclass
from collections import namedtuple

World = namedtuple("World", "particle walls")


@dataclass(frozen=True, order=True)
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


@dataclass(frozen=True)
class Wall:
    p1: Position
    p2: Position

    def draw(self, surface):
        pygame.draw.line(surface, (255, 255, 255), self.p1.tup, self.p2.tup, 2)


@dataclass(frozen=True)
class Particle:
    pos: Position

    def draw(self, surface, walls):
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(self.pos.tup, (1, 1)))

        self._draw_walls(surface, walls)

    def _draw_walls(self, surface, walls, num=10):
        dirs = []
        for x in range(-num, num + 1):
            for y in range(-num, num + 1):
                x, y = x / num, y / num
                if x == y == 0:
                    continue
                dirs.append(Position(x, y))

        for direc in dirs:
            best = None
            dist = 10 ** 10
            for wall in walls:
                pos = self.intersect(direc, wall)
                if not pos:
                    continue
                dist_ = self.pos.dist(pos)
                if dist_ < dist:
                    dist = dist_
                    best = pos

            if best is not None:
                pygame.draw.line(surface, (255, 255, 0), self.pos.tup, best.tup)

    def intersect(self, direc, wall):
        x1, y1 = wall.p1
        x2, y2 = wall.p2
        x3, y3 = self.pos
        x4, y4 = self.pos + direc
        t_t = (x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)
        t_n = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        if t_n == 0:
            return
        t = t_t / t_n
        if not 0 <= t <= 1:
            return

        u_t = (x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)
        u_n = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        u = -u_t / u_n
        return Position(x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def _input(events):
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit(0)
        else:
            return event


def draw_world(surface, world):
    width, height = 512, 512
    particle = world.particle
    walls = world.walls

    surface.fill((0, 0, 0))

    for wall in walls:
        wall.draw(surface)

    particle.draw(surface, walls)

    pygame.display.flip()


def rand():
    return random.randint(0, 512)


def randpos():
    return Position(rand(), rand())


def randline():
    return randpos(), randpos()


def nextpoint(pos):
    x, y = pos.tup
    nx = 3 * pnoise2(x / 600, y / 600, 2)
    ny = 3 * pnoise2(x / 700, y / 700, 2)
    nx += x
    ny += y

    nx = min(max(25, nx), 500)
    ny = min(max(25, ny), 500)
    return Position(nx, ny)


def game_loop(surface):
    world = World(Particle(Position(100, 100)), [Wall(*randline()) for _ in range(4)])
    walls = world.walls
    while True:
        evt = _input(pygame.event.get())
        if evt is None or evt.type != pygame.MOUSEMOTION:
            pos = nextpoint(world.particle.pos)
        else:
            pos = evt.pos
        world = World(Particle(Position(*pos)), walls)
        draw_world(surface, world)


def main():
    width, height = 512, 512

    pygame.init()
    pygame.display.set_mode((width, height))
    screen = pygame.display.get_surface()

    game_loop(screen)


if __name__ == "__main__":
    main()
