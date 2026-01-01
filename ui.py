import random
import pygame


class TitleRenderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.background = pygame.Surface((width, height))
        self._build_background()

    def _build_background(self):
        for y in range(self.height):
            shade = 10 + int(40 * (y / self.height))
            pygame.draw.line(self.background, (shade, shade, shade + 10), (0, y), (self.width, y))
        for x in range(0, self.width, 6):
            pygame.draw.rect(self.background, (20, 10, 20), (x, 0, 3, self.height))
        for _ in range(200):
            nx = random.randint(0, self.width - 1)
            ny = random.randint(0, self.height - 1)
            self.background.set_at((nx, ny), (35, 35, 45))

    def draw(self, surface, title_font, font, blink):
        surface.blit(self.background, (0, 0))
        title = title_font.render("거짓의 방", True, (240, 240, 240))
        subtitle = font.render("사실은 전부 무대였다.", True, (180, 180, 180))
        hint = font.render("ENTER 시작 / E 도움말 / ESC 종료", True, (200, 200, 200)) if blink else None
        surface.blit(title, (self.width // 2 - title.get_width() // 2, 52))
        surface.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 78))
        if hint:
            surface.blit(hint, (self.width // 2 - hint.get_width() // 2, 110))


class HUD:
    def __init__(self, font):
        self.font = font

    def draw(self, surface, player, charge_ratio):
        for i in range(player.max_hp):
            x = 8 + i * 12
            y = 6
            color = (200, 60, 80) if i < player.hp else (50, 50, 50)
            pygame.draw.rect(surface, color, pygame.Rect(x, y, 10, 8))
        text = self.font.render(f"HP {player.hp}/{player.max_hp}  조각 {player.score}", True, (200, 200, 200))
        surface.blit(text, (8, 18))
        bar_w = 120
        bar_h = 6
        x = 8
        y = surface.get_height() - 14
        pygame.draw.rect(surface, (30, 30, 40), pygame.Rect(x, y, bar_w, bar_h))
        fill = int(bar_w * charge_ratio)
        pygame.draw.rect(surface, (120, 200, 240), pygame.Rect(x, y, fill, bar_h))
        label = self.font.render("차지", True, (180, 180, 180))
        surface.blit(label, (x + bar_w + 6, y - 4))


def draw_help(surface, font):
    surface.fill((12, 12, 20))
    lines = [
        "도움말",
        "이동: A/D 또는 ←/→",
        "점프: SPACE (꾹 누르면 차지, 떼면 더 높게)",
        "공격: 마우스 좌클릭",
        "대시: SHIFT + 방향키",
        "도움말: E",
        "도움말 종료: ↑ 또는 ESC",
        "재시작: R (게임오버/클리어)",
        "피해: 피격 시 1초 무적(깜빡임)",
        "목표: 맵 끝 커튼에 도달",
        "팁: 구멍 아래로 떨어지면 즉사",
    ]
    y = 20
    for idx, line in enumerate(lines):
        color = (220, 220, 220) if idx == 0 else (180, 180, 180)
        text = font.render(line, True, color)
        surface.blit(text, (20, y))
        y += 18
