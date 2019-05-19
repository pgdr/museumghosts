import random

from .geometry import Position, Line


def _rand(max_):
    return random.randint(0, max_)


def randpos(size):
    return Position(_rand(size.x), _rand(size.y))


def randline(size):
    return Line(randpos(size), randpos(size))
