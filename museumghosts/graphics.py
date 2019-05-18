import pygame
import time


def draw_world(surface, world, speed, direction):
    player = world.player
    ghosts = world.ghosts
    walls = world.walls

    surface.fill((0, 0, 0))

    for wall in walls:
        wall.draw(surface)

    player.draw(surface, world=world, speed=speed, direction=direction)
    for explosion in world.explosions:
        explosion.draw(surface, time.time())

    pygame.display.flip()
