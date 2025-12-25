import pygame

from game import Game
from world import VIEW_PIXEL_H, VIEW_PIXEL_W


SCALE = 3


def main():
    pygame.init()
    pygame.display.set_caption("거짓의 방")
    screen = pygame.display.set_mode((VIEW_PIXEL_W * SCALE, VIEW_PIXEL_H * SCALE))
    render_surface = pygame.Surface((VIEW_PIXEL_W, VIEW_PIXEL_H))
    game = Game(screen, render_surface)
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()
