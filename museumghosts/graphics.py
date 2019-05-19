import pygame
from .geometry import Line, intersects


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


def draw_vision(surface, player, walls, fov, rot):
    for direc in player.direcs(fov, rot):
        best = None
        dist = 2000
        for wall in walls:
            pos = intersects(wall, Line(player.pos, player.pos + direc), ray=True)
            if not pos:
                continue
            dist_ = pos.dist(player.pos)
            if dist_ < dist:
                dist = dist_
                best = pos

        if best is not None:
            pygame.draw.line(surface, (255, 255, 255), player.pos.tup, best.tup, 2)


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
