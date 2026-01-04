import random
import pygame

from setting import HELP_BOX_ALPHA


class TitleRenderer:
    def __init__(self, width, height, background=None, title_image=None):
        self.width = width
        self.height = height
        self.background = pygame.Surface((width, height))
        self._build_background()
        self.background_image = background
        self.title_image = title_image

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

    def draw(self, surface, title_font, font, blink, difficulty):
        if self.background_image:
            bg = pygame.transform.scale(self.background_image, (self.width, self.height))
            surface.blit(bg, (0, 0))
        else:
            surface.blit(self.background, (0, 0))
        hint_text = "ENTER 시작 / 1 EASY / 2 HARD / E 도움말 / ESC 종료"
        hint = font.render(hint_text, True, (200, 200, 200)) if blink else None
        mode_text = "현재 난이도: EASY" if difficulty == "easy" else "현재 난이도: HARD"
        mode = font.render(mode_text, True, (220, 200, 200))
        if self.title_image:
            title = pygame.transform.scale(self.title_image, (self.width, self.title_image.get_height()))
            surface.blit(title, (self.width // 2 - title.get_width() // 2, 40))
        surface.blit(mode, (self.width // 2 - mode.get_width() // 2, 100))
        if hint:
            surface.blit(hint, (self.width // 2 - hint.get_width() // 2, 122))


class HUD:
    def __init__(self, font):
        self.font = font

    def draw(self, surface, player, play_time):
        for i in range(player.max_hp):
            x = 8 + i * 12
            y = 6
            color = (200, 60, 80) if i < player.hp else (50, 50, 50)
            pygame.draw.rect(surface, color, pygame.Rect(x, y, 10, 8))
        timer_text = self.font.render(f"TIME {play_time:05.2f}", True, (200, 200, 200))
        surface.blit(timer_text, (surface.get_width() - timer_text.get_width() - 8, 6))


class HintBox:
    def __init__(self, font):
        self.font = font

    def draw(self, surface):
        lines = [
            "R 공격",
            "SHIFT 달리기",
            "SHIFT+방향 대시",
        ]
        padding = 3
        width = max(self.font.size(line)[0] for line in lines) + padding * 2
        height = len(lines) * (self.font.get_height() + 2) + padding * 2
        x = surface.get_width() - width - 8
        y = surface.get_height() - height - 8
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        panel.fill((20, 20, 30, HELP_BOX_ALPHA))
        surface.blit(panel, (x, y))
        for idx, line in enumerate(lines):
            text = self.font.render(line, True, (200, 200, 200))
            surface.blit(text, (x + padding, y + padding + idx * (self.font.get_height() + 2)))


class HintBox:
    def __init__(self, font):
        self.font = font

    def draw(self, surface):
        lines = [
            "R 공격",
            "SHIFT 달리기",
            "SHIFT+방향 대시",
        ]
        padding = 4
        width = max(self.font.size(line)[0] for line in lines) + padding * 2
        height = len(lines) * 14 + padding * 2
        x = surface.get_width() - width - 8
        y = surface.get_height() - height - 8
        pygame.draw.rect(surface, (20, 20, 30), pygame.Rect(x, y, width, height))
        for idx, line in enumerate(lines):
            text = self.font.render(line, True, (200, 200, 200))
            surface.blit(text, (x + padding, y + padding + idx * 14))


def draw_help(surface, font):
    surface.fill((12, 12, 20))
    lines = [
        "도움말",
        "이동: A/D 또는 ←/→",
        "점프: SPACE (더블 점프 가능)",
        "공격: R",
        "대시: SHIFT + 방향키",
        "달리기: SHIFT",
        "도움말: E",
        "도움말 종료: ↑ 또는 ESC",
        "재시작: R (클리어 화면)",
        "피해: 피격 시 0.5초 무적(깜빡임)",
        "목표: 맵 끝 커튼에 도달",
        "팁: 구멍 아래로 떨어지면 체크포인트로 복귀",
    ]
    y = 20
    for idx, line in enumerate(lines):
        color = (220, 220, 220) if idx == 0 else (180, 180, 180)
        text = font.render(line, True, color)
        surface.blit(text, (20, y))
        y += 18
