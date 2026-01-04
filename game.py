import random
import pygame

from assets import build_assets, load_font
from entities import (
    Player,
    Enemy1,
    Enemy2,
    Heart,
    Particle,
    DirectorBoss,
    DancerBoss,
    JudgeBoss,
    ClownBoss,
    ArchivistBoss,
)
from platformer_world import (
    TILE_SIZE,
    LEVEL_PIXEL_H,
    LEVEL_PIXEL_W,
    KILL_Y,
    STAGE_LINES,
    build_map,
    build_solid_rects,
    build_signs,
    build_checkpoints,
    STAGE_SPAWNS,
)
from ui import HUD, HintBox, TitleRenderer, draw_help
from setting import BOSS_ACTIVATION_DISTANCE


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
        self.hearts = []
        self.signs = build_signs()
        self.checkpoints = build_checkpoints()
        self.goal_rect = pygame.Rect(LEVEL_PIXEL_W - TILE_SIZE * 3, TILE_SIZE * 4, TILE_SIZE, TILE_SIZE * 3)
        self.boss = None
        self.level_width = LEVEL_PIXEL_W
        self.camera_x = 0

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
        self.hint_box = HintBox(self.font)
        self.title_renderer = TitleRenderer(self.render_surface.get_width(), self.render_surface.get_height())
        self.camera_x = 0
        self.stage_text = ""
        self.stage_timer = 0
        self.message = ""
        self.attack_hitboxes = []
        self.particles = []
        self.notice = ""
        self.notice_timer = 0
        self.hitstop_timer = 0
        self.shake_timer = 0
        self.shake_strength = 0
        self.play_time = 0
        self.clear_time = 0
        self.difficulty = "easy"
        self.enemy_speed_scale = 1.0
        self.enemy_damage = 1
        self.respawn_point = pygame.Vector2(self.player.rect.x, self.player.rect.y)
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
        self.hitstop_timer = 0
        self.shake_timer = 0
        self.shake_strength = 0
        self.play_time = 0
        self.clear_time = 0
        self.respawn_point = pygame.Vector2(self.player.rect.x, self.player.rect.y)
        self.apply_difficulty()
        stage = STAGE_SPAWNS["stage_1"]
        self.world.enemies = []
        for kind, x, y in stage["enemies"]:
            if kind == "enemy1":
                self.world.enemies.append(Enemy1(x, y, speed=60 * self.enemy_speed_scale))
            else:
                self.world.enemies.append(Enemy2(x, y, speed=85 * self.enemy_speed_scale))
        self.world.hearts = [Heart(x, y) for x, y in stage["hearts"]]
        self.world.boss = self._create_boss(stage["boss"])

    def _create_boss(self, boss_data):
        boss_map = {
            "director": DirectorBoss,
            "dancer": DancerBoss,
            "judge": JudgeBoss,
            "clown": ClownBoss,
            "archivist": ArchivistBoss,
        }
        boss_cls = boss_map.get(boss_data["name"], DirectorBoss)
        return boss_cls(boss_data["x"], boss_data["y"])

    def apply_difficulty(self):
        if self.difficulty == "hard":
            self.enemy_speed_scale = 1.25
            self.enemy_damage = 2
        else:
            self.enemy_speed_scale = 0.9
            self.enemy_damage = 1

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
                        self.reset_stage()
                    elif event.key == pygame.K_e:
                        self.state = STATE_HELP
                    elif event.key == pygame.K_1:
                        self.difficulty = "easy"
                        self.state = STATE_PLAYING
                        self.reset_stage()
                    elif event.key == pygame.K_2:
                        self.difficulty = "hard"
                        self.state = STATE_PLAYING
                        self.reset_stage()
                elif self.state == STATE_HELP:
                    if event.key == pygame.K_UP:
                        self.state = STATE_TITLE
                elif self.state in (STATE_GAME_OVER, STATE_VICTORY):
                    if event.key == pygame.K_r:
                        self.state = STATE_TITLE
                        self.reset_stage()
                elif self.state == STATE_PLAYING:
                    if event.key == pygame.K_e:
                        self.try_read_sign()
                if self.state == STATE_PLAYING and event.key == pygame.K_SPACE:
                    if not self.player.start_jump_charge():
                        self.player.queue_jump()
            if event.type == pygame.KEYUP:
                if self.state == STATE_PLAYING and event.key == pygame.K_SPACE:
                    self.player.handle_jump_release()
            if event.type == pygame.KEYDOWN and self.state == STATE_PLAYING:
                if event.key == pygame.K_r:
                    hitbox = self.player.create_attack_hitbox()
                    if hitbox:
                        self.attack_hitboxes.append(hitbox)
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

        if self.hitstop_timer > 0:
            self.hitstop_timer = max(0, self.hitstop_timer - dt)
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
                    self.hitstop_timer = 0.05
                    self.shake_timer = 0.2
                    self.shake_strength = 4
                    if random.random() < 0.35:
                        self.world.hearts.append(Heart(enemy.rect.centerx, enemy.rect.centery))
                    break
            if self.player.rect.colliderect(enemy.rect):
                if self.player.take_damage(self.enemy_damage):
                    self.player.vel.x = -self.player.facing * 160
                    self.player.vel.y = -140
                    self.shake_timer = 0.2
                    self.shake_strength = 3
                if self.player.hp <= 0:
                    self.respawn_player()
            if not enemy.alive or enemy.rect.y > KILL_Y:
                if enemy in self.world.enemies:
                    self.world.enemies.remove(enemy)

        if self.world.boss and self.world.boss.alive:
            boss_distance = abs(self.player.rect.centerx - self.world.boss.rect.centerx)
            boss_active = boss_distance <= BOSS_ACTIVATION_DISTANCE or self.player.rect.x > LEVEL_PIXEL_W - TILE_SIZE * 18
            if boss_active:
                self.world.boss.update(dt, self.world, self.player)
            for attack in self.world.boss.attacks:
                if attack.rect.colliderect(self.player.rect):
                    if self.player.take_damage(attack.damage):
                        self.shake_timer = 0.2
                        self.shake_strength = 4
            if self.player.rect.colliderect(self.world.boss.rect) and self.player.take_damage(1):
                self.player.vel.x = -self.player.facing * 180
                self.player.vel.y = -160
            if self.world.boss.hp <= 0:
                self.state = STATE_VICTORY
                self.clear_time = self.play_time
                self.message = f"막이 내렸다. 등급 {self.calculate_rank()}"

        for heart in list(self.world.hearts):
            heart.update(dt, self.world, self.player)
            if self.player.rect.colliderect(heart.rect):
                self.player.hp = min(self.player.max_hp, self.player.hp + 1)
                self.world.hearts.remove(heart)

        for particle in list(self.particles):
            particle.update(dt)
            if not particle.alive():
                self.particles.remove(particle)

        for checkpoint in self.world.checkpoints:
            if self.player.rect.colliderect(checkpoint.rect):
                if self.respawn_point.x != checkpoint.rect.x or self.respawn_point.y != checkpoint.rect.y:
                    self.respawn_point = pygame.Vector2(checkpoint.rect.x, checkpoint.rect.y)
                    self.notice = f"{checkpoint.label} 저장됨"
                    self.notice_timer = 1.5

        if self.player.rect.y > KILL_Y:
            self.respawn_player()

        if self.player.rect.colliderect(self.world.goal_rect) and (not self.world.boss or not self.world.boss.alive):
            self.state = STATE_VICTORY
            self.clear_time = self.play_time
            self.message = f"막이 내렸다. 등급 {self.calculate_rank()}"

        if self.stage_timer > 0:
            self.stage_timer -= dt

        if self.notice_timer > 0:
            self.notice_timer -= dt

        if self.shake_timer > 0:
            self.shake_timer = max(0, self.shake_timer - dt)

        self.play_time += dt
        self.update_camera()

    def calculate_rank(self):
        if self.clear_time <= 55:
            return "S"
        if self.clear_time <= 80:
            return "A"
        if self.clear_time <= 110:
            return "B"
        return "C"

    def respawn_player(self):
        self.player.hp = self.player.max_hp
        self.player.rect.x = int(self.respawn_point.x)
        self.player.rect.y = int(self.respawn_point.y)
        self.player.vel.update(0, 0)
        self.player.invincible_timer = 0.5
        self.player.dash_invincible_timer = 0
        self.player.charging_jump = False
        self.player.jump_charge = 0
        self.player.on_ground = False
        self.camera_x = max(0, min(self.player.rect.centerx - self.render_surface.get_width() // 2, LEVEL_PIXEL_W - self.render_surface.get_width()))
        self.notice = "다시 연기했다."
        self.notice_timer = 1.4

    def spawn_blood(self, x, y):
        for _ in range(12):
            self.particles.append(Particle(x, y))

    def update_camera(self):
        view_w = self.render_surface.get_width()
        target = self.player.rect.centerx - view_w // 2
        self.camera_x = max(0, min(target, LEVEL_PIXEL_W - view_w))
        self.world.camera_x = self.camera_x

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

        for checkpoint in self.world.checkpoints:
            color = (200, 200, 120) if self.respawn_point.x == checkpoint.rect.x else (120, 140, 160)
            pygame.draw.rect(self.render_surface, color, checkpoint.rect.move(-self.camera_x, 0))

        for heart in self.world.hearts:
            self.render_surface.blit(self.assets["heart"], (heart.rect.x - self.camera_x, heart.rect.y))

        for enemy in self.world.enemies:
            if isinstance(enemy, Enemy1):
                frames = self.assets["enemy1_frames"]
                frame_index = int(enemy.anim_timer * 10) % len(frames)
            else:
                frames = self.assets["enemy2_frames"]
                frame_index = int(enemy.anim_timer * 8) % len(frames)
            frame = frames[frame_index]
            self.render_surface.blit(frame, (enemy.rect.x - self.camera_x, enemy.rect.y))

        if self.world.boss and self.world.boss.alive:
            pygame.draw.rect(self.render_surface, self.world.boss.color, self.world.boss.rect.move(-self.camera_x, 0))
            for telegraph in self.world.boss.telegraphs:
                pygame.draw.rect(self.render_surface, telegraph.color, telegraph.rect.move(-self.camera_x, 0), 1)
            for attack in self.world.boss.attacks:
                pygame.draw.rect(self.render_surface, attack.color, attack.rect.move(-self.camera_x, 0))

        goal = self.assets["goal"]
        self.render_surface.blit(goal, (self.world.goal_rect.x - self.camera_x, self.world.goal_rect.y))

        if not self.player.should_blink():
            frame_index = 0
            if abs(self.player.vel.x) > 10 and self.player.on_ground:
                run_frames = self.assets["player_run_frames"]
                frame_index = int(self.player.anim_timer * 12) % len(run_frames)
                frame = run_frames[frame_index]
            else:
                frame = self.assets["player_idle_frames"][0]
            if self.player.facing < 0:
                frame = pygame.transform.flip(frame, True, False)
            self.render_surface.blit(frame, (self.player.rect.x - self.camera_x - 7, self.player.rect.y - 6))

        for hitbox in self.attack_hitboxes:
            attack_image = self.assets["attack"]
            if self.player.facing < 0:
                attack_image = pygame.transform.flip(attack_image, True, False)
            self.render_surface.blit(attack_image, (hitbox.rect.x - self.camera_x, hitbox.rect.y))

        for particle in self.particles:
            self.render_surface.blit(self.assets["blood"], (particle.pos.x - self.camera_x, particle.pos.y))

    def draw(self):
        self.render_surface.fill((10, 10, 20))
        if self.state == STATE_TITLE:
            blink = (pygame.time.get_ticks() // 600) % 2 == 0
            self.title_renderer.draw(self.render_surface, self.big_font, self.font, blink, self.difficulty)
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
            charge_ratio = 0
            if self.player.jump_charge_max > 0:
                charge_ratio = min(1.0, self.player.jump_charge / self.player.jump_charge_max)
            self.hud.draw(self.render_surface, self.player, charge_ratio, self.player.jump_charge_full, self.play_time)
            self.hint_box.draw(self.render_surface)
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

        shake_x = 0
        shake_y = 0
        if self.shake_timer > 0:
            shake_x = random.randint(-self.shake_strength, self.shake_strength)
            shake_y = random.randint(-self.shake_strength, self.shake_strength)
        scaled = pygame.transform.scale(self.render_surface, self.screen.get_size())
        self.screen.blit(scaled, (shake_x, shake_y))
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
