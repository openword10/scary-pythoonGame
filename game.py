import random
import pygame

from assets import build_assets
from entities import Player, Projectile
from items import ItemLibrary, ItemPickup
from ui import HUD
from world import LEVEL_PIXEL_H, LEVEL_PIXEL_W, TILE_SIZE, Level
from items import ItemLibrary
from ui import HUD
from world import ROOM_PIXEL_H, ROOM_PIXEL_W, TILE_SIZE, WorldMap


STATE_TITLE = "title"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_VICTORY = "victory"


ENTRY_LINES = [
    "컷. 다시.",
    "웃어. 장면이 망가져.",
    "관객은 없었다.",
    "무대는 텅 비어 있었다.",
    "대사는 거짓으로 울린다.",
]


class Game:
    def __init__(self, screen, render_surface):
        self.screen = screen
        self.render_surface = render_surface
        self.clock = pygame.time.Clock()
        self.assets = build_assets()
        self.font = pygame.font.SysFont("malgungothic", 12)
        self.state = STATE_TITLE
        self.item_library = ItemLibrary()
        self.level = Level(self.item_library)
        self.floor = 1
        self.player = Player(TILE_SIZE * 2, LEVEL_PIXEL_H - TILE_SIZE * 4)
        self.world = WorldMap(3, self.item_library)
        self.floor = 1
        self.current_room_coord = self.world.start
        self.current_room = self.world.get_room(self.current_room_coord)
        self.player = Player(ROOM_PIXEL_W // 2, ROOM_PIXEL_H // 2)
        self.hud = HUD(self.font, self.assets)
        self.entry_timer = 0
        self.entry_text = ""
        self.hint_text = ""
        self.projectile_speed_bonus = 0
        self.enemy_speed_bonus = 0
        self.camera = pygame.Vector2(0, 0)
        self.reset_level(first_time=True)

    def reset_level(self, first_time=False):
        if first_time:
            self.level = Level(self.item_library)
        self.reset_room(self.current_room, first_time=True)

    def reset_room(self, room, first_time=False):
        if first_time or not room.visited:
            room.spawn_enemies(difficulty=1 if self.floor == 1 else 2)
        room.visited = True
        room.projectiles = []
        self.entry_text = random.choice(ENTRY_LINES)
        self.entry_timer = 1.2

    def reveal_next_room_hint(self):
        self.hint_text = "무대 끝에서 커튼이 열린다"

    def boost_projectiles(self):
        self.projectile_speed_bonus += 60

    def boost_enemies(self):
        self.enemy_speed_bonus += 10

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.state == STATE_TITLE:
                    self.state = STATE_PLAYING
                elif self.state in (STATE_GAME_OVER, STATE_VICTORY):
                    self.restart_game()
                elif self.state == STATE_PLAYING and event.key in (pygame.K_SPACE, pygame.K_w):
                    self.player.jump()
                elif self.state == STATE_PLAYING and event.key == pygame.K_r:
                    if self.player.room_reset_charges > 0:
                        self.player.room_reset_charges -= 1
                        self.reset_level(first_time=True)
        return True

    def restart_game(self):
        self.state = STATE_TITLE
        self.level = Level(self.item_library)
        self.player = Player(TILE_SIZE * 2, LEVEL_PIXEL_H - TILE_SIZE * 4)
        self.floor = 1
        self.entry_text = ""
        self.hint_text = ""
        self.projectile_speed_bonus = 0
        self.enemy_speed_bonus = 0
        self.reset_level(first_time=True)

    def update(self, dt):
        if self.state != STATE_PLAYING:
            return

        keys = pygame.key.get_pressed()
        move_dir = pygame.Vector2(0, 0)
        if keys[pygame.K_a]:
            move_dir.x -= 1
        if keys[pygame.K_d]:
            move_dir.x += 1
        self.player.move(dt, move_dir, self.level)

        shoot_dir = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT]:
            shoot_dir.x -= 1
        if keys[pygame.K_RIGHT]:
            shoot_dir.x += 1
        if keys[pygame.K_UP]:
            shoot_dir.y -= 1
        if keys[pygame.K_DOWN]:
            shoot_dir.y += 1
        if shoot_dir.length_squared() > 0 and self.player.can_shoot():
            projectile = Projectile(
                self.player.rect.centerx - 3,
                self.player.rect.centery - 3,
                shoot_dir,
                speed=260 + self.projectile_speed_bonus,
            )
            self.level.projectiles.append(projectile)
            self.player.reset_shoot()

        self.player.update(dt, self.level, self.player)

        for projectile in list(self.level.projectiles):
            projectile.update(dt, self.level, self.player)
            if not projectile.alive:
                self.level.projectiles.remove(projectile)

        for enemy in list(self.level.enemies):
            enemy.speed_bonus = self.enemy_speed_bonus
            enemy.update(dt, self.level, self.player)
            if enemy.rect.colliderect(self.player.rect):
                self.player.take_damage(1)
            if not enemy.alive:
                self.level.enemies.remove(enemy)
                if random.random() < 0.25:
                    item = self.item_library.random_item()
                    self.level.pickups.append(ItemPickup(enemy.rect.x, enemy.rect.y, item))

        for projectile in list(self.level.projectiles):
            for enemy in self.level.enemies:
                if projectile.rect.colliderect(enemy.rect):
                    enemy.take_damage(1)
                    projectile.alive = False
            if not projectile.alive and projectile in self.level.projectiles:
                self.level.projectiles.remove(projectile)

        for pickup in self.level.pickups:
            if not pickup.collected and pickup.rect.colliderect(self.player.rect):
                pickup.collected = True
                pickup.item.apply(self.player, self, self.level)
                self.player.item_texts.append(f"{pickup.item.name}: {pickup.item.description}")

        self.level.pickups = [pickup for pickup in self.level.pickups if not pickup.collected]

        if self.player.hp <= 0:
            self.state = STATE_GAME_OVER

        if self.level.update_clear_state() and self.player.rect.colliderect(self.level.exit_rect):
            self.state = STATE_VICTORY

        if self.entry_timer > 0:
            self.entry_timer -= dt

        self.update_camera()

    def update_camera(self):
        target_x = self.player.rect.centerx - self.render_surface.get_width() // 2
        target_y = self.player.rect.centery - self.render_surface.get_height() // 2
        self.camera.x = max(0, min(target_x, LEVEL_PIXEL_W - self.render_surface.get_width()))
        self.camera.y = max(0, min(target_y, LEVEL_PIXEL_H - self.render_surface.get_height()))

    def draw_level(self):
        floor = self.assets["floor"]
        wall_image = self.assets["wall"]
        for y in range(0, LEVEL_PIXEL_H, TILE_SIZE):
            for x in range(0, LEVEL_PIXEL_W, TILE_SIZE):
                self.render_surface.blit(floor, (x - self.camera.x, y - self.camera.y))

        for solid in self.level.solid_rects:
            self.render_surface.blit(wall_image, (solid.x - self.camera.x, solid.y - self.camera.y))

        for px, py, prop_type in self.level.props:
            key = f"prop_{prop_type}"
            self.render_surface.blit(self.assets[key], (px - self.camera.x, py - self.camera.y))

        exit_color = (80, 140, 200)
        pygame.draw.rect(self.render_surface, exit_color, self.level.exit_rect.move(-self.camera.x, -self.camera.y))

    def draw(self):
        self.render_surface.fill((15, 15, 20))
        if self.state == STATE_TITLE:
            self.draw_title()
        elif self.state == STATE_PLAYING:
            self.draw_level()
            for pickup in self.level.pickups:
                self.render_surface.blit(
                    self.assets[pickup.item.icon_key],
                    (pickup.rect.x - self.camera.x, pickup.rect.y - self.camera.y),
                )
            for projectile in self.level.projectiles:
                projectile.draw(self.render_surface, self.assets["bullet"], self.camera)
            for enemy in self.level.enemies:
                if enemy.__class__.__name__ == "Chaser":
                    enemy.draw(self.render_surface, self.assets["chaser"], self.camera)
                else:
                    enemy.draw(self.render_surface, self.assets["dasher"], self.camera)
            self.player.draw(self.render_surface, self.assets["player"], self.camera)
            if self.entry_timer > 0:
                text = self.font.render(self.entry_text, True, (220, 200, 180))
                self.render_surface.blit(text, (self.render_surface.get_width() // 2 - text.get_width() // 2, 6))
            self.hud.draw(self.render_surface, self.player, self)
        elif self.state == STATE_GAME_OVER:
            self.draw_end("게임 오버")
        elif self.state == STATE_VICTORY:
            self.draw_end("막이 내렸다")

        scaled = pygame.transform.scale(self.render_surface, self.screen.get_size())
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()

    def draw_title(self):
        title = self.font.render("거짓의 방", True, (240, 240, 240))
        subtitle = self.font.render("ENTER 아무 키 - A/D 이동, SPACE 점프", True, (180, 180, 180))
        self.render_surface.blit(title, (self.render_surface.get_width() // 2 - title.get_width() // 2, 90))
        self.render_surface.blit(subtitle, (self.render_surface.get_width() // 2 - subtitle.get_width() // 2, 110))

    def draw_end(self, message):
        text = self.font.render(message, True, (240, 120, 120))
        sub = self.font.render("아무 키로 다시", True, (180, 180, 180))
        self.render_surface.blit(text, (self.render_surface.get_width() // 2 - text.get_width() // 2, 90))
        self.render_surface.blit(sub, (self.render_surface.get_width() // 2 - sub.get_width() // 2, 110))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            running = self.handle_events()
            self.update(dt)
            self.draw()
