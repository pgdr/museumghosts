import itertools
from .geometry import intersects, Line, Position, line_segments


def _rect_line_iterator(rect):
    upperleft, lowerright = rect
    x1, y1 = upperleft
    x2, y2 = lowerright

    yield from (
        Line(Position(x1, y1), Position(x2, y1)),
        Line(Position(x2, y1), Position(x2, y2)),
        Line(Position(x1, y1), Position(x1, y2)),
        Line(Position(x1, y2), Position(x2, y2)),
    )


def _points_in_lines(lines):
    for line in lines:
        yield from line


def _vertex_iterator(world):
    for wall in world.walls:
        yield from wall.line


def _pair_iterator(world):
    yield from itertools.product(_vertex_iterator(world), _vertex_iterator(world))


def _preprocess_rect(world, upperleft, lowerright):
    """From a rect, gives all O(n**2) points on the rect that might have
       different views than the corner points.  Includes also the corner
       points.

    """
    EPSILON = Position(0.01, 0.01)
    x1, y1 = upperleft
    x2, y2 = lowerright
    rect_lines = _rect_line_iterator((upperleft, lowerright))
    point_collection = set(_points_in_lines(rect_lines))
    for p1, p2 in _pair_iterator(world):
        for rect_edge in rect_lines:
            point = intersects(Line(p1, p2), rect_edge, ray=True)
            if point:
                point_collection.add(point + EPSILON)
                point_collection.add(point - EPSILON)

    return point_collection


def _gen_rects(size, cellsize=100):
    """Discretizes the world given a size.
       Yields rectangles that cover world.
    """
    x = 0
    y = 0
    while x < size.x:
        while y < size.y:
            yield Line(Position(x, y), Position(x + cellsize, y + cellsize))
            y += cellsize
        y = 0
        x += cellsize
    return []


def _visible_walls(world, rect, point_collection):
    """Given a set of points, compute (union of) set of walls
       that can be seen from any point in the collection.

       Also includes any wall that crosses the rect boundary.
    """

    visible = set()

    # first all the visible walls
    for p in point_collection:
        # for wall in world.walls:
        segs = line_segments(p, world.walls, visible=True)
        for wall in world.walls:
            for seg in segs:
                p1, p2 = seg
                if intersects(
                    wall,
                    Line(p1 + Position(0.01, 0.01), p2 - Position(0.01, 0.01)),
                    ray=False,
                ):
                    visible.add(wall)

    # all walls intersecting the rect
    for wall in world.walls:
        for line in _rect_line_iterator(rect):
            if intersects(wall, line, ray=False):
                visible.add(wall)

    return visible


def preprocess(world):
    """Returns a dict from rectangles to a set of walls that are
       potentially visible from somewhere in the rect.
    """
    visible_walls = {}
    for rect in _gen_rects(world.size):
        point_collection = _preprocess_rect(world, *rect)
        visible_walls[(rect.p1, rect.p2)] = _visible_walls(
            world, rect, point_collection
        )
    return visible_walls
