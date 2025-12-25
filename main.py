import pygame

from game import Game


INTERNAL_WIDTH = 400
INTERNAL_HEIGHT = 225
SCALE = 4


def main():
    pygame.init()
    pygame.display.set_caption("거짓의 방")
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)
    render_surface = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
    game = Game(screen, render_surface)
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()
