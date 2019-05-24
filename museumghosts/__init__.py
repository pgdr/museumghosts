import pygame
from .game import SIZE, game_loop

from .gameobjects import World, Wall, Particle, Ghost, Explosion
from .forgetlist import Forgetlist
from .geometry import Position, Line, line_point_collection, line_segments


def main():

    pygame.init()
    pygame.display.set_mode((SIZE.x, SIZE.y))
    pygame.display.set_caption("Museum guard")
    screen = pygame.display.get_surface()
    # pygame.mouse.set_visible(False)  # this should be a crosshair

    game_loop(screen)


if __name__ == "__main__":
    main()
