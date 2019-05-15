import math
import sys
import random
import pygame
from noise import pnoise1

from dataclasses import dataclass
from collections import namedtuple

World = namedtuple("World", "particle antiparticle walls")

WIDTH = 1000
HEIGHT = 600


def intersects(line1, line2, ray=True):
    x1, y1 = line1.p1
    x2, y2 = line1.p2
    x3, y3 = line2.p1
    x4, y4 = line2.p2

    t_n = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    if t_n == 0:
        return

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / t_n
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / t_n

    if not 0 <= t <= 1:
        return
    test = u > 0 if ray else 0 <= u <= 1
    if test:
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        return Position(x, y)


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
        return Position(min(max(8, self.x), WIDTH - 8), min(max(8, self.y), HEIGHT - 8))

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

    def draw(self, surface, walls=tuple(), color=(255, 0, 0)):
        self._draw_walls(surface, walls)
        pygame.draw.circle(surface, color, round(self.pos), 4)

    def _draw_walls(self, surface, walls):
        for direc in self.direcs():
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


def draw_ghost(surface, world):
    pos = world.particle
    apos = world.antiparticle
    walls = world.walls
    line = Wall(pos.pos, apos.pos)
    for wall in walls:
        if intersects(line, wall, ray=False):
            return False
    pygame.draw.circle(surface, (255, 0, 255), round(apos.pos), 4)


def _input(events):
    for event in events:
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            sys.exit(0)
        else:
            return event


def draw_world(surface, world):
    particle = world.particle
    antiparticle = world.antiparticle
    walls = world.walls

    surface.fill((0, 0, 0))

    for wall in walls:
        wall.draw(surface)

    particle.draw(surface, walls=walls)
    draw_ghost(surface, world)

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
    particle = Particle(Position(100, 100))
    antiparticle = Particle(Position(200, 200))

    bnw = Position(0, 0)
    bne = Position(WIDTH, 0)
    bsw = Position(0, HEIGHT)
    bse = Position(WIDTH, HEIGHT)

    boundary = [Wall(bnw, bne), Wall(bne, bse), Wall(bse, bsw), Wall(bsw, bnw)]

    world = World(
        particle, antiparticle, boundary + [Wall(*randline()) for _ in range(10)]
    )

    xoff = 10.0
    yoff = 100.0

    walls = world.walls
    while True:
        evt = _input(pygame.event.get())
        pos = Position(WIDTH * pnoise1(xoff) // 100, HEIGHT * pnoise1(yoff) // 100)

        xoff += 10.01
        yoff += 20.01
        antiparticle = Particle((antiparticle.pos + pos).normalize())
        if evt is not None and evt.type == pygame.MOUSEMOTION:
            pos = Position(*evt.pos).normalize()
            particle = Particle(Position(*pos))

        world = World(particle, antiparticle, walls)
        if particle.pos.dist(antiparticle.pos) < 5:
            print("You won")
            exit("0")
        draw_world(surface, world)


def main():
    width, height = WIDTH, HEIGHT

    pygame.init()
    pygame.display.set_mode((width, height))
    screen = pygame.display.get_surface()

    game_loop(screen)


if __name__ == "__main__":
    main()
