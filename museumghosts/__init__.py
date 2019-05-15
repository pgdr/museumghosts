import math
import sys
import random
import pygame
from noise import pnoise1

from dataclasses import dataclass
from collections import namedtuple

World = namedtuple("World", "particle ghosts walls")

from .util import Position
from .util import intersects

WIDTH = 1000
HEIGHT = 600


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


def draw_ghosts(surface, world):
    """Draw all ghosts within view."""
    pos = world.particle
    walls = world.walls

    for ghost in world.ghosts:
        line = Wall(pos.pos, ghost.pos)
        for wall in walls:
            if intersects(line, wall, ray=False):
                return False
        pygame.draw.circle(surface, (255, 0, 255), round(ghost.pos), 4)


def _input(events):
    for event in events:
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            sys.exit(0)
        else:
            return event


def draw_world(surface, world):
    particle = world.particle
    ghosts = world.ghosts
    walls = world.walls

    surface.fill((0, 0, 0))

    for wall in walls:
        wall.draw(surface)

    particle.draw(surface, walls=walls)
    draw_ghosts(surface, world)

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
    ghosts = [Particle(Position(200, 200))]

    bnw = Position(0, 0)
    bne = Position(WIDTH, 0)
    bsw = Position(0, HEIGHT)
    bse = Position(WIDTH, HEIGHT)

    boundary = [Wall(bnw, bne), Wall(bne, bse), Wall(bse, bsw), Wall(bsw, bnw)]

    world = World(particle, ghosts, boundary + [Wall(*randline()) for _ in range(10)])

    xoff = 10.0
    yoff = 100.0

    walls = world.walls
    while True:
        evt = _input(pygame.event.get())
        pos = Position(WIDTH * pnoise1(xoff) // 100, HEIGHT * pnoise1(yoff) // 100)

        xoff += 10.01
        yoff += 20.01
        ghosts = [Particle(ghosts[0].pos + pos)]
        if evt is not None and evt.type == pygame.MOUSEMOTION:
            pos = Position(*evt.pos)
            particle = Particle(Position(*pos))

        world = World(particle, ghosts, walls)
        if particle.pos.dist(ghosts[0].pos) < 5:
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
