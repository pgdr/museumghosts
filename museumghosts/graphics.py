import pygame
from .geometry import Line, intersects

from .geometry import line_segments


def draw_world(surface, world, speed, now):
    player = world.player
    walls = world.walls

    surface.fill((0, 0, 0))
    bg = pygame.image.load("floor.png")
    bg_x, bg_y = bg.get_rect().size
    for i in range(3):
        for j in range(3):
            surface.blit(bg, (bg_x * i, bg_y * j))

    for wall in walls:
        wall.draw(surface)

    vision_surface = pygame.Surface(world.size.tup)
    vision_surface.fill((100, 100, 100))
    vision_surface.set_alpha(100)

    player.draw(vision_surface, world=world, speed=speed)

    # invert vision polygon
    pixels = pygame.surfarray.pixels2d(vision_surface)
    pixels ^= 2 ** 32 - 1
    del pixels

    surface.blit(vision_surface, (0, 0), None, pygame.BLEND_RGB_SUB)

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
            surface.blit(ghost.sprite, (ghost.pos - ghost.size / 2).tup)
