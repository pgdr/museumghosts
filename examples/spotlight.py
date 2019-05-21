import pygame

SIZE = (480, 320)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
pygame.init()
pygame.display.set_mode(SIZE)
bg = pygame.image.load("bg.png")
surface = pygame.display.get_surface()


pos = (0, 0)
while True:
    surface.blit(bg, (0, 0))

    evts = pygame.event.get()

    for evt in evts:
        if evt.type == pygame.KEYDOWN:
            pygame.quit()
            exit()
        if evt.type == pygame.MOUSEMOTION:
            pos = evt.pos
    s2 = pygame.Surface(SIZE)
    s2.fill(BLACK)
    pygame.draw.circle(s2, WHITE, pos, 50)
    s2.set_alpha(100)

    pixels = pygame.surfarray.pixels2d(s2)
    pixels ^= 2 ** 32 - 1
    del pixels

    surface.blit(s2, (0, 0), None, pygame.BLEND_RGB_SUB)

    pygame.display.flip()
