import pygame

from game import Game


INTERNAL_WIDTH = 400
INTERNAL_HEIGHT = 225
SCALE = 4


def main():
    # Pygame 초기화 및 창 설정
    pygame.init()
    pygame.display.set_caption("거짓의 방")
    info = pygame.display.Info()
    # 전체 화면 크기에 맞춰 표시 (프레임 없는 창)
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)
    # 내부 렌더 해상도는 고정 크기로 유지
    render_surface = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
    game = Game(screen, render_surface)
    # 메인 루프 실행
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()
