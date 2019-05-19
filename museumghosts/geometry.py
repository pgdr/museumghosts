from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other: "Position") -> "Position":
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Position") -> "Position":
        return Position(self.x - other.x, self.y - other.y)

    def __truediv__(self, scalar: int) -> "Position":
        return Position(self.x / scalar, self.y / scalar)

    def __iter__(self):
        yield self.x
        yield self.y

    def dist(self, other: "Position") -> float:
        xs = (self.x - other.x) ** 2
        ys = (self.y - other.y) ** 2
        return math.sqrt(xs + ys)

    @property
    def tup(self):
        return (self.x, self.y)

    def __round__(self):
        return int(self.x), int(self.y)

    def normalize(self, size, padding=24):
        return Position(
            min(max(padding, self.x), size.x - padding),
            min(max(padding, self.y), size.y - padding),
        )


@dataclass(frozen=True)
class Line:
    p1: Position
    p2: Position

    def __iter__(self):
        yield self.p1
        yield self.p2


def intersects(line1, line2, ray=True):
    if not isinstance(line1, Line):
        line1 = line1.line
    if not isinstance(line2, Line):
        line2 = line2.line

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
    test = u >= 0 if ray else 0 <= u <= 1
    if test:
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        return Position(x, y)
