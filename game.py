import random
import pygame

from assets import build_assets, load_font
from entities import Player, Enemy1, Enemy2, Coin
from platformer_world import TILE_SIZE, LEVEL_PIXEL_H, LEVEL_PIXEL_W, STAGE_LINES, build_map, build_solid_rects
from ui import HUD, TitleRenderer


STATE_TITLE = "title"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_VICTORY = "victory"


class World:
    def __init__(self):
        self.tiles = build_map()
        self.solids = build_solid_rects(self.tiles)
        self.enemies = []
        self.coins = []
        self.goal_rect = pygame.Rect(LEVEL_PIXEL_W - TILE_SIZE * 3, TILE_SIZE * 5, TILE_SIZE, TILE_SIZE * 2)

    def is_solid_at(self, x, y):
        if x < 0 or y < 0 or x >= LEVEL_PIXEL_W or y >= LEVEL_PIXEL_H:
            return True
        tile_x = int(x // TILE_SIZE)
        tile_y = int(y // TILE_SIZE)
        try:
            return self.tiles[tile_y][tile_x] == 1
        except Exception:
            return True


class Game:
    def __init__(self, screen, render_surface):
        self.screen = screen
        self.render_surface = render_surface
        self.clock = pygame.time.Clock()
        self.assets = build_assets()
        self.font = load_font(12)
        self.big_font = load_font(20)
        self.state = STATE_TITLE
        self.world = World()
        self.player = Player(TILE_SIZE * 2, LEVEL_PIXEL_H - TILE_SIZE * 4)
        self.hud = HUD(self.font)
        self.title_renderer = TitleRenderer(self.render_surface.get_width(), self.render_surface.get_height())
        self.camera_x = 0
        self.stage_text = ""
        self.stage_timer = 0
        self.message = ""
        self.reset_stage()

    def reset_stage(self):
        self.world = World()
        self.player = Player(TILE_SIZE * 2, LEVEL_PIXEL_H - TILE_SIZE * 4)
        self.camera_x = 0
        self.stage_text = random.choice(STAGE_LINES)
        self.stage_timer = 1.4
        self.message = ""
        self.world.enemies = [
            Enemy1(TILE_SIZE * 12, LEVEL_PIXEL_H - TILE_SIZE * 4),
            Enemy1(TILE_SIZE * 32, LEVEL_PIXEL_H - TILE_SIZE * 4),
            Enemy2(TILE_SIZE * 48, LEVEL_PIXEL_H - TILE_SIZE * 4),
            Enemy1(TILE_SIZE * 60, LEVEL_PIXEL_H - TILE_SIZE * 4),
            Enemy2(TILE_SIZE * 68, LEVEL_PIXEL_H - TILE_SIZE * 4),
        ]
        self.world.coins = [
            Coin(TILE_SIZE * 10, LEVEL_PIXEL_H - TILE_SIZE * 6),
            Coin(TILE_SIZE * 20, LEVEL_PIXEL_H - TILE_SIZE * 6),
            Coin(TILE_SIZE * 36, LEVEL_PIXEL_H - TILE_SIZE * 6),
            Coin(TILE_SIZE * 55, LEVEL_PIXEL_H - TILE_SIZE * 6),
            Coin(TILE_SIZE * 70, LEVEL_PIXEL_H - TILE_SIZE * 6),
        ]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if self.state == STATE_TITLE and event.key == pygame.K_RETURN:
                    self.state = STATE_PLAYING
                elif self.state in (STATE_GAME_OVER, STATE_VICTORY) and event.key == pygame.K_r:
                    self.state = STATE_TITLE
                    self.reset_stage()
        return True

    def update(self, dt):
        if self.state != STATE_PLAYING:
            return

        keys = pygame.key.get_pressed()
        self.player.handle_input(dt, keys)
        self.player.try_jump()
        self.player.apply_gravity(dt, keys[pygame.K_SPACE])
        self.player.move_and_collide(dt, self.world.solids)
        self.player.update(dt, self.world, self.player)

        for enemy in list(self.world.enemies):
            enemy.update(dt, self.world, self.player)
            if self.player.rect.colliderect(enemy.rect):
                if self.player.vel.y > 0 and self.player.rect.bottom - enemy.rect.top < 8:
                    self.player.vel.y = -120
                    enemy.alive = False
                else:
                    self.player.hp -= 1
                    if self.player.hp <= 0:
                        self.state = STATE_GAME_OVER
                        self.message = "무대는 끝났다."
            if not enemy.alive:
                self.world.enemies.remove(enemy)

        for coin in list(self.world.coins):
            if self.player.rect.colliderect(coin.rect):
                self.player.score += 1
                self.world.coins.remove(coin)

        if self.player.rect.colliderect(self.world.goal_rect):
            self.state = STATE_VICTORY
            self.message = "막이 내렸다."

        if self.stage_timer > 0:
            self.stage_timer -= dt

        self.update_camera()

    def update_camera(self):
        view_w = self.render_surface.get_width()
        target = self.player.rect.centerx - view_w // 2
        self.camera_x = max(0, min(target, LEVEL_PIXEL_W - view_w))

    def draw_world(self):
        bg = self.assets["bg"]
        for y in range(0, LEVEL_PIXEL_H, TILE_SIZE):
            for x in range(0, LEVEL_PIXEL_W, TILE_SIZE):
                self.render_surface.blit(bg, (x - self.camera_x, y))

        floor = self.assets["tile_floor"]
        wall = self.assets["tile_wall"]
        for y, row in enumerate(self.world.tiles):
            for x, tile in enumerate(row):
                if tile == 1:
                    self.render_surface.blit(wall, (x * TILE_SIZE - self.camera_x, y * TILE_SIZE))
                else:
                    self.render_surface.blit(floor, (x * TILE_SIZE - self.camera_x, y * TILE_SIZE))

        for coin in self.world.coins:
            self.render_surface.blit(self.assets["coin"], (coin.rect.x - self.camera_x, coin.rect.y))

        for enemy in self.world.enemies:
            image_key = "enemy1" if isinstance(enemy, Enemy1) else "enemy2"
            self.render_surface.blit(self.assets[image_key], (enemy.rect.x - self.camera_x, enemy.rect.y))

        goal = self.assets["goal"]
        self.render_surface.blit(goal, (self.world.goal_rect.x - self.camera_x, self.world.goal_rect.y))

        self.render_surface.blit(self.assets["player"], (self.player.rect.x - self.camera_x, self.player.rect.y))

    def draw(self):
        self.render_surface.fill((10, 10, 20))
        if self.state == STATE_TITLE:
            blink = (pygame.time.get_ticks() // 600) % 2 == 0
            self.title_renderer.draw(self.render_surface, self.big_font, self.font, blink)
        else:
            self.draw_world()
            if self.stage_timer > 0:
                text = self.font.render(self.stage_text, True, (220, 200, 180))
                self.render_surface.blit(text, (8, 8))
            self.hud.draw(self.render_surface, self.player, self)
            if self.state in (STATE_GAME_OVER, STATE_VICTORY):
                end_text = self.big_font.render(self.message, True, (220, 140, 140))
                self.render_surface.blit(
                    end_text,
                    (self.render_surface.get_width() // 2 - end_text.get_width() // 2, 80),
                )
                hint = self.font.render("R 재시작 / ESC 종료", True, (200, 200, 200))
                self.render_surface.blit(
                    hint,
                    (self.render_surface.get_width() // 2 - hint.get_width() // 2, 110),
                )

        scaled = pygame.transform.scale(self.render_surface, self.screen.get_size())
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            running = self.handle_events()
            try:
                self.update(dt)
            except Exception as exc:
                print(f"[오류] {exc}")
                self.state = STATE_GAME_OVER
                self.message = "장면이 깨졌다."
            self.draw()
