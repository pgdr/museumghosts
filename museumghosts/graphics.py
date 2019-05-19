import pygame
from .geometry import Line, intersects

from .geometry import line_point_collection, line_segments


def draw_world(surface, world, speed, now):
    player = world.player
    walls = world.walls

    surface.fill((0, 0, 0))

    for wall in walls:
        wall.draw(surface)

    player.draw(surface, world=world, speed=speed)
    for explosion in world.explosions:
        explosion.draw(surface, now)

    pygame.display.flip()


def draw_vision(surface, world):
    player = world.player
    walls = world.walls
    for segment in line_segments(world):
        triangle = player.pos.tup, segment.p1.tup, segment.p2.tup, player.pos.tup
        pygame.draw.polygon(surface, (255, 255, 255), triangle)


def draw_ghosts(surface, world):
    """Draw all ghosts within view."""
    pos = world.player
    walls = world.walls
    for ghost in world.ghosts:
        if ghost.is_dead:
            # I see dead ghosts
            surface.blit(ghost.sprite, (ghost.pos - ghost.size / 2).tup)
            continue

        line = Line(pos.pos, ghost.pos)
        for wall in walls:
            if intersects(line, wall, ray=False):
                break
        else:
            # TODO check that line falls within fov
            surface.blit(ghost.sprite, (ghost.pos - ghost.size / 2).tup)
