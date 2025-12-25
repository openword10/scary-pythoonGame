import pygame

from game import Game


INTERNAL_WIDTH = 400
INTERNAL_HEIGHT = 225
SCALE = 4


def main():
    pygame.init()
    pygame.display.set_caption("거짓의 방")
    screen = pygame.display.set_mode((INTERNAL_WIDTH * SCALE, INTERNAL_HEIGHT * SCALE))
    render_surface = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
    game = Game(screen, render_surface)
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()
