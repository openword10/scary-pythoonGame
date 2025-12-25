import random
import pygame

from assets import build_assets, load_font
from entities import Player, Enemy1, Enemy2, Coin, AttackHitbox, Particle
from platformer_world import TILE_SIZE, LEVEL_PIXEL_H, LEVEL_PIXEL_W, KILL_Y, STAGE_LINES, build_map, build_solid_rects, build_signs
from ui import HUD, TitleRenderer, draw_help


STATE_TITLE = "title"
STATE_HELP = "help"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_VICTORY = "victory"


class World:
    def __init__(self):
        self.tiles = build_map()
        self.solids = build_solid_rects(self.tiles)
        self.enemies = []
        self.coins = []
        self.signs = build_signs()
        self.goal_rect = pygame.Rect(LEVEL_PIXEL_W - TILE_SIZE * 3, TILE_SIZE * 4, TILE_SIZE, TILE_SIZE * 3)

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
        self.help_requested = False
        self.attack_hitboxes = []
        self.particles = []
        self.notice = ""
        self.notice_timer = 0
        self.reset_stage()

    def reset_stage(self):
        self.world = World()
        self.player = Player(TILE_SIZE * 2, LEVEL_PIXEL_H - TILE_SIZE * 4)
        self.camera_x = 0
        self.stage_text = random.choice(STAGE_LINES)
        self.stage_timer = 1.4
        self.message = ""
        self.notice = ""
        self.notice_timer = 0
        self.attack_hitboxes = []
        self.particles = []
        self.world.enemies = [
            Enemy1(TILE_SIZE * 18, LEVEL_PIXEL_H - TILE_SIZE * 4),
            Enemy1(TILE_SIZE * 32, LEVEL_PIXEL_H - TILE_SIZE * 4),
            Enemy2(TILE_SIZE * 48, LEVEL_PIXEL_H - TILE_SIZE * 4),
            Enemy1(TILE_SIZE * 60, LEVEL_PIXEL_H - TILE_SIZE * 4),
            Enemy2(TILE_SIZE * 72, LEVEL_PIXEL_H - TILE_SIZE * 4),
        ]
        self.world.coins = [
            Coin(TILE_SIZE * 10, LEVEL_PIXEL_H - TILE_SIZE * 6),
            Coin(TILE_SIZE * 22, LEVEL_PIXEL_H - TILE_SIZE * 6),
            Coin(TILE_SIZE * 40, LEVEL_PIXEL_H - TILE_SIZE * 6),
            Coin(TILE_SIZE * 55, LEVEL_PIXEL_H - TILE_SIZE * 6),
            Coin(TILE_SIZE * 70, LEVEL_PIXEL_H - TILE_SIZE * 6),
        ]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_HELP:
                        self.state = STATE_TITLE
                        return True
                    return False
                if self.state == STATE_TITLE:
                    if event.key == pygame.K_RETURN:
                        self.state = STATE_PLAYING
                    elif event.key == pygame.K_e:
                        self.state = STATE_HELP
                elif self.state == STATE_HELP:
                    if event.key == pygame.K_UP:
                        self.state = STATE_TITLE
                elif self.state in (STATE_GAME_OVER, STATE_VICTORY):
                    if event.key == pygame.K_r:
                        self.state = STATE_TITLE
                        self.reset_stage()
                elif self.state == STATE_PLAYING:
                    if event.key == pygame.K_r:
                        hitbox = self.player.create_attack_hitbox()
                        if hitbox:
                            self.attack_hitboxes.append(hitbox)
                    if event.key == pygame.K_e:
                        self.try_read_sign()
        return True

    def try_read_sign(self):
        for sign in self.world.signs:
            if self.player.rect.colliderect(sign.rect.inflate(20, 20)):
                self.notice = sign.text
                self.notice_timer = 2.2
                return

    def update(self, dt):
        if self.state != STATE_PLAYING:
            return

        keys = pygame.key.get_pressed()
        self.player.handle_input(dt, keys)
        self.player.try_jump()
        self.player.try_dash(keys)
        self.player.apply_gravity(dt, keys[pygame.K_SPACE])
        self.player.move_and_collide(dt, self.world.solids)
        self.player.update(dt, self.world, self.player)

        for hitbox in list(self.attack_hitboxes):
            hitbox.update(dt)
            if not hitbox.active:
                self.attack_hitboxes.remove(hitbox)

        for enemy in list(self.world.enemies):
            enemy.update(dt, self.world, self.player)
            for hitbox in self.attack_hitboxes:
                if hitbox.rect.colliderect(enemy.rect):
                    enemy.alive = False
                    self.spawn_blood(enemy.rect.centerx, enemy.rect.centery)
            if self.player.rect.colliderect(enemy.rect):
                self.player.hp -= 1
                if self.player.hp <= 0:
                    self.state = STATE_GAME_OVER
                    self.message = "무대는 끝났다."
            if not enemy.alive or enemy.rect.y > KILL_Y:
                if enemy in self.world.enemies:
                    self.world.enemies.remove(enemy)

        for coin in list(self.world.coins):
            if self.player.rect.colliderect(coin.rect):
                self.player.score += 1
                self.world.coins.remove(coin)

        for particle in list(self.particles):
            particle.update(dt)
            if not particle.alive():
                self.particles.remove(particle)

        if self.player.rect.y > KILL_Y:
            self.player.hp = 0
            self.state = STATE_GAME_OVER
            self.message = "구멍 아래엔 아무것도 없었다."

        if self.player.rect.colliderect(self.world.goal_rect):
            self.state = STATE_VICTORY
            self.message = "막이 내렸다."

        if self.stage_timer > 0:
            self.stage_timer -= dt

        if self.notice_timer > 0:
            self.notice_timer -= dt

        self.update_camera()

    def spawn_blood(self, x, y):
        for _ in range(12):
            self.particles.append(Particle(x, y))

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

        for sign in self.world.signs:
            pygame.draw.rect(self.render_surface, (80, 80, 120), sign.rect.move(-self.camera_x, 0))

        for coin in self.world.coins:
            self.render_surface.blit(self.assets["coin"], (coin.rect.x - self.camera_x, coin.rect.y))

        for enemy in self.world.enemies:
            image_key = "enemy1" if isinstance(enemy, Enemy1) else "enemy2"
            self.render_surface.blit(self.assets[image_key], (enemy.rect.x - self.camera_x, enemy.rect.y))

        goal = self.assets["goal"]
        self.render_surface.blit(goal, (self.world.goal_rect.x - self.camera_x, self.world.goal_rect.y))

        self.render_surface.blit(self.assets["player"], (self.player.rect.x - self.camera_x, self.player.rect.y))

        for hitbox in self.attack_hitboxes:
            self.render_surface.blit(self.assets["attack"], (hitbox.rect.x - self.camera_x, hitbox.rect.y))

        for particle in self.particles:
            self.render_surface.blit(self.assets["blood"], (particle.pos.x - self.camera_x, particle.pos.y))

    def draw(self):
        self.render_surface.fill((10, 10, 20))
        if self.state == STATE_TITLE:
            blink = (pygame.time.get_ticks() // 600) % 2 == 0
            self.title_renderer.draw(self.render_surface, self.big_font, self.font, blink)
        elif self.state == STATE_HELP:
            draw_help(self.render_surface, self.font)
        else:
            self.draw_world()
            if self.stage_timer > 0:
                text = self.font.render(self.stage_text, True, (220, 200, 180))
                self.render_surface.blit(text, (8, 8))
            if self.notice_timer > 0:
                note = self.font.render(self.notice, True, (220, 220, 200))
                self.render_surface.blit(note, (8, 26))
            self.hud.draw(self.render_surface, self.player)
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
