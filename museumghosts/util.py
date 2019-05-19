import random

from noise import pnoise1

from .geometry import Position, Line

_PERLINX = 10.0
_PERLINY = 2000.0


def perlin(size, x, y):
    global _PERLINX, _PERLINY
    x = size.x * pnoise1(_PERLINX + x) // 100
    y = size.y * pnoise1(_PERLINY + y) // 100
    _PERLINX += 1.01
    _PERLINY += 0.01
    pos = Position(x, y)
    return pos


def _rand(max_):
    return random.randint(0, max_)


def randpos(size):
    return Position(_rand(size.x), _rand(size.y))


def randline(size):
    return Line(randpos(size), randpos(size))
