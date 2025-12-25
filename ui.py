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
        hint = font.render("ENTER 시작 / ESC 종료", True, (200, 200, 200)) if blink else None
        surface.blit(title, (self.width // 2 - title.get_width() // 2, 60))
        surface.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 86))
        if hint:
            surface.blit(hint, (self.width // 2 - hint.get_width() // 2, 118))


class HUD:
    def __init__(self, font):
        self.font = font

    def draw(self, surface, player, floor, room_coord, hint_text):
        for i in range(player.max_hp):
            x = 8 + i * 10
            y = 6
            color = (200, 60, 80) if i < player.hp else (50, 50, 50)
            pygame.draw.rect(surface, color, pygame.Rect(x, y, 8, 8))
        text = self.font.render(f"층 {floor}  방 {room_coord}", True, (200, 200, 200))
        surface.blit(text, (8, 20))
        y = 34
        for text in player.item_texts[-4:]:
            rendered = self.font.render(text, True, (160, 160, 190))
            surface.blit(rendered, (8, y))
            y += 12
        if hint_text:
            hint = self.font.render(hint_text, True, (200, 180, 120))
            surface.blit(hint, (8, surface.get_height() - 16))
