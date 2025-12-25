import sys
import pygame

from game import Game
from world import VIEW_PIXEL_H, VIEW_PIXEL_W


SCALE = 3
REQUIRED_PYTHON = (3, 12)
REQUIRED_PYGAME = (2, 5, 0)


def _check_versions():
    if sys.version_info < REQUIRED_PYTHON:
        raise RuntimeError(f"Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}+ 필요")
    if pygame.version.vernum < REQUIRED_PYGAME:
        raise RuntimeError("pygame 2.5.0+ 필요")


def main():
    pygame.init()
    _check_versions()
    pygame.display.set_caption("거짓의 방")
    screen = pygame.display.set_mode((VIEW_PIXEL_W * SCALE, VIEW_PIXEL_H * SCALE))
    render_surface = pygame.Surface((VIEW_PIXEL_W, VIEW_PIXEL_H))
    game = Game(screen, render_surface)
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()
