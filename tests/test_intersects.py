from museumghosts import (
    World,
    Particle,
    Position,
    Wall,
    Line,
    Position,
    line_point_collection,
    line_segments,
)


def linepts(x1, y1, x2, y2):
    return Line(Position(x1, y1), Position(x2, y2))


def _world():
    SIZE = Position(640, 480)
    player = Particle(Position(SIZE.x // 2, SIZE.y // 2))
    ghosts = []

    bnw = Position(0, 0)
    bne = Position(SIZE.x, 0)
    bsw = Position(0, SIZE.y)
    bse = Position(SIZE.x, SIZE.y)

    boundary = [
        Wall(Line(bnw, bne)),
        Wall(Line(bne, bse)),
        Wall(Line(bse, bsw)),
        Wall(Line(bsw, bnw)),
    ]

    world = World(SIZE, player, ghosts, boundary, [], [])
    return world


def test_create():
    _world()


def test_line_point_intersect_keys():
    topline = Line(Position(5, 1), Position(12, 1))
    botline = Line(Position(1, 3), Position(8, 3))
    pov = Particle(Position(4, 9))
    w = _world().but(walls=[Wall(topline), Wall(botline)], player=pov)
    isects = line_point_collection(w.player.pos, w.walls)

    assert set(isects.keys()) == set([topline, botline])


def test_line_point_intersect_types():
    topline = Line(Position(5, 1), Position(12, 1))
    botline = Line(Position(1, 3), Position(8, 3))
    pov = Particle(Position(4, 9))
    w = _world().but(walls=[Wall(topline), Wall(botline)], player=pov)
    isects = line_point_collection(w.player.pos, w.walls)
    for k, v in isects.items():
        assert isinstance(k, Line)
        for pos in v:
            assert isinstance(pos, Position)


def test_line_point_intersect():
    topline = Line(Position(5, 1), Position(12, 1))
    botline = Line(Position(1, 3), Position(8, 3))
    pov = Particle(Position(4, 9))
    w = _world().but(walls=[Wall(topline), Wall(botline)], player=pov)
    isects = line_point_collection(w.player.pos, w.walls)

    assert Position(9.3333333333333333, 1) in isects[topline]
    assert Position(4.75, 3) in isects[botline]


def test_line_segments():
    topline = Line(Position(5, 1), Position(12, 1))
    botline = Line(Position(1, 3), Position(8, 3))
    pov = Particle(Position(4, 9))
    w = _world().but(walls=[Wall(topline), Wall(botline)], player=pov)
    linesegments = list(line_segments(w.player.pos, w.walls, visible=False))

    for l in linesegments:
        assert isinstance(l, Line)
        for p in l:
            assert isinstance(p, Position)

    topline1 = Line(Position(5, 1), Position(9.3333333333333333, 1))
    topline2 = Line(Position(9.3333333333333333, 1), Position(12, 1))

    botline1 = Line(Position(1, 3), Position(4.75, 3))
    botline2 = Line(Position(4.75, 3), Position(8, 3))

    assert set([topline1, topline2, botline1, botline2]) == set(linesegments)


def test_line_segments_visible():
    topline = Line(Position(5, 1), Position(12, 1))
    botline = Line(Position(1, 3), Position(8, 3))
    pov = Particle(Position(4, 9))
    w = _world().but(walls=[Wall(topline), Wall(botline)], player=pov)
    linesegments = list(line_segments(w.player.pos, w.walls, visible=True))

    for l in linesegments:
        assert isinstance(l, Line)
        for p in l:
            assert isinstance(p, Position)

    topline2 = Line(Position(9.3333333333333333, 1), Position(12, 1))

    botline1 = Line(Position(1, 3), Position(4.75, 3))
    botline2 = Line(Position(4.75, 3), Position(8, 3))

    assert set([topline2, botline1, botline2]) == set(linesegments)


def test_lines_intersecting():
    l1 = linepts(1, 1, 2, 3)
    l2 = linepts(1, 3, 2, 1)
    pov = Position(3, 2)
    w = _world().but(walls=[Wall(l1), Wall(l2)], player=Particle(pov))

    col = line_point_collection(w.player.pos, w.walls)
    assert len(col) == 2
    assert Position(x=1.8, y=2.6) in col[l1]
    assert Position(x=1.8, y=1.4) in col[l2]
    assert Position(1.5, 2) in col[l2]
    assert len(col[l1]) == 4
    assert len(col[l2]) == 4
