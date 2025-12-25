import pygame

from game import Game
from world import ROOM_PIXEL_H, ROOM_PIXEL_W


SCALE = 3


def main():
    pygame.init()
    pygame.display.set_caption("거짓의 방")
    screen = pygame.display.set_mode((ROOM_PIXEL_W * SCALE, ROOM_PIXEL_H * SCALE))
    render_surface = pygame.Surface((ROOM_PIXEL_W, ROOM_PIXEL_H))
    game = Game(screen, render_surface)
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()
