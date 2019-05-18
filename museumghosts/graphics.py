import pygame
from .util import Line, intersects


def draw_world(surface, world, speed, direction, now):
    player = world.player
    walls = world.walls

    surface.fill((0, 0, 0))

    for wall in walls:
        wall.draw(surface)

    player.draw(surface, world=world, speed=speed, direction=direction)
    for explosion in world.explosions:
        explosion.draw(surface, now)

    pygame.display.flip()


def draw_ghosts(surface, world, fov, rot):
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
