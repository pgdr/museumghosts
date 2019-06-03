import math


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other: "Position") -> "Position":
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Position") -> "Position":
        return Position(self.x - other.x, self.y - other.y)

    def __truediv__(self, scalar: int) -> "Position":
        return Position(self.x / scalar, self.y / scalar)

    def __floordiv__(self, scalar: int) -> "Position":
        return Position(self.x // scalar, self.y // scalar)

    def __mul__(self, scalar: int) -> "Position":
        return Position(self.x * scalar, self.y * scalar)

    def __iter__(self):
        yield self.x
        yield self.y

    def flip_hor(self):
        return Position(-self.x, self.y)

    def flip_vert(self):
        return Position(self.x, -self.y)

    def dist(self, other: "Position") -> float:
        xs = (self.x - other.x) ** 2
        ys = (self.y - other.y) ** 2
        return math.sqrt(xs + ys)

    def but(self, x=None, y=None):
        x = self.x if x is None else x
        y = self.y if y is None else y
        return Position(x, y)

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

    def __eq__(self, other):
        if not isinstance(other, Position):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __lt__(self, other):
        return self.tup < other.tup


class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __iter__(self):
        yield self.p1
        yield self.p2

    def __eq__(self, other):
        if not isinstance(other, Line):
            return NotImplemented
        return self.p1 == other.p1 and self.p2 == other.p2

    def __hash__(self):
        return hash((hash(self.p1), hash(self.p2)))

    def __repr__(self):
        return "Line({}, {})".format(self.p1, self.p2)


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


def _crossing_lines(lines):
    N = len(lines)
    for i in range(N):
        l1 = lines[i]
        for j in range(i + 1, N):
            l2 = lines[j]
            p = intersects(l1, l2, ray=False)
            if p:
                yield (l1, p)
                yield (l2, p)


def line_point_collection(pov, walls):
    """Return all points that intersects the ray formed from
       the player to an edge.
    """
    lines = [wall.line for wall in walls]
    point_collection = {line: set([line.p1, line.p2]) for line in lines}

    for l, p in _crossing_lines(lines):
        point_collection[l].add(p)

    for line in lines:
        for edge in line:
            ray = Line(pov, edge)
            for wall in lines:
                if wall == line:
                    continue
                ipoint = intersects(wall, ray, ray=True)
                if ipoint:
                    point_collection[wall].add(ipoint)
    return point_collection


def _is_point_visible(pov, walls, belonging_wall, point):
    ray = Line(pov, point)
    for wall in walls:
        if wall.line == belonging_wall:
            continue
        if intersects(ray, wall, ray=False):
            return False
    return True


def _mid_point(line):
    return Position((line.p1.x + line.p2.x) / 2, (line.p1.y + line.p2.y) / 2)


def line_segments(pov, walls, visible=True):
    """Return all the line segments that are formed by the intersection points
       from the visible ray.
    """
    point_collection = line_point_collection(pov, walls)

    for wall, isects in point_collection.items():
        line = sorted(isects)
        for idx in range(len(line) - 1):
            segment = Line(line[idx], line[idx + 1])
            if visible:
                if _is_point_visible(pov, walls, wall, _mid_point(segment)):
                    yield segment
            else:
                yield segment


def crosses_wall(walls, ray):
    for wall in walls:
        if intersects(wall, ray, ray=False):
            return wall
    return None
