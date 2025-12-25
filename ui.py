import pygame


class HUD:
    def __init__(self, font, assets):
        self.font = font
        self.assets = assets

    def draw(self, surface, player, game):
        self._draw_hearts(surface, player)
        self._draw_floor(surface, game)
        self._draw_items(surface, player)
        self._draw_hint(surface, game)

    def _draw_hearts(self, surface, player):
        heart = self.assets["ui_heart"]
        for i in range(player.max_hp):
            x = 8 + i * 10
            y = 6
            if i < player.hp:
                surface.blit(heart, (x, y))
            else:
                gray = pygame.Surface(heart.get_size(), pygame.SRCALPHA)
                gray.fill((40, 40, 40))
                surface.blit(gray, (x, y))

    def _draw_floor(self, surface, game):
        text = self.font.render(f"층 {game.floor}  위치 X:{int(game.player.rect.x)}", True, (200, 200, 200))
        surface.blit(text, (8, 20))

    def _draw_items(self, surface, player):
        y = 34
        for text in player.item_texts[-4:]:
            rendered = self.font.render(text, True, (160, 160, 190))
            surface.blit(rendered, (8, y))
            y += 12

    def _draw_hint(self, surface, game):
        if game.hint_text:
            text = self.font.render(game.hint_text, True, (200, 180, 120))
            surface.blit(text, (8, surface.get_height() - 16))
