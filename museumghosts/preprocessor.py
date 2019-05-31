import itertools
from .geometry import intersects


def _vertex_iterator(world):
    for wall in world.walls:
        yield from wall.line


def _pair_iterator(world):
    yield from product(_vertex_iterator(world), _vertex_iterator(world))


def _preprocess_rect(world, upperleft, lowerright):
    """From a rect, gives all O(n**2) points on the rect that might have
       different views than the corner points.  Includes also the corner
       points.

    """
    x1, y1 = upperleft
    x2, y2 = lowerright
    point_collection = set(
        [
            Position(x1, y1),
            Position(x2, y1),
            Position(x2, y1),
            Position(x2, y2),
            Position(x1, y1),
            Position(x1, y2),
            Position(x1, y2),
            Position(x2, y2),
        ]
    )  # set of all points on the rectangle
    rect = (
        Line(Position(x1, y1), Position(x2, y1)),
        Line(Position(x2, y1), Position(x2, y2)),
        Line(Position(x1, y1), Position(x1, y2)),
        Line(Position(x1, y2), Position(x2, y2)),
    )
    for p1, p2 in _pair_iterator(world):
        for rect_edge in rect:
            point = intersects(Line(p1, p2), rect_edge, ray=True)
            if point:
                point_collection.add(point)

    return point_collection


def _get_rects(size):
    """Discretizes the world given a size.  Yields rectangles that cover world."""
    return []


def _visible_walls(world, point_collection):
    """Given a set of points, compute (union of) set of walls
       that can be seen from any point in the collection.
    """
    visible = set()
    for p in point_collection:
        for wall in world.walls:
            pass  # TODO implement
    return visible


def preprocess(world):
    """Returns a dict from rectangles to a set of walls that are visible from somewhere in the rect"""
    rect_visibility = {}
    for rect in _gen_rects(world.size):
        point_collection = _preprocess_rect(world, *rect)
        visible_walls[rect] = _visible_walls(world, point_collection)
    return {}
