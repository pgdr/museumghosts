import pygame
from .game import SIZE, game_loop


def main():

    pygame.init()
    pygame.display.set_mode((SIZE.x, SIZE.y))
    screen = pygame.display.get_surface()

    game_loop(screen)


if __name__ == "__main__":
    main()
