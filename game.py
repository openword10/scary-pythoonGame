import random
import pygame

from assets import build_assets, load_font
from entities import Player, Projectile
from items import ItemLibrary
from ui import HUD, TitleRenderer
from world import ROOM_PIXEL_H, ROOM_PIXEL_W, TILE_SIZE, ENTRY_LINES, WorldMap


STATE_TITLE = "title"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_VICTORY = "victory"


class Game:
    def __init__(self, screen, render_surface):
        self.screen = screen
        self.render_surface = render_surface
        self.clock = pygame.time.Clock()
        self.assets = build_assets()
        self.font = load_font(12)
        self.big_font = load_font(20)
        self.state = STATE_TITLE
        self.item_library = ItemLibrary()
        self.world = WorldMap(3, self.item_library)
        self.floor = 1
        self.current_room_coord = self.world.start
        self.current_room = self.world.get_room(self.current_room_coord)
        self.player = Player(ROOM_PIXEL_W // 2, ROOM_PIXEL_H // 2)
        self.entry_timer = 0
        self.entry_text = ""
        self.hint_text = ""
        self.projectile_speed_bonus = 0
        self.enemy_speed_bonus = 0
        self.title_renderer = TitleRenderer(ROOM_PIXEL_W, ROOM_PIXEL_H)
        self.hud = HUD(self.font)
        self.error_message = ""
        self.reset_room(self.current_room, first_time=True)

    def reset_room(self, room, first_time=False):
        if first_time or not room.visited:
            room.spawn_enemies(difficulty=1 if self.floor == 1 else 2)
        room.visited = True
        room.projectiles = []
        self.entry_text = random.choice(ENTRY_LINES)
        self.entry_timer = 1.2

    def reveal_next_room_hint(self):
        neighbors = [coord for coord in self.world.neighbors(self.current_room_coord).values() if self.world.in_bounds(coord)]
        if neighbors:
            self.hint_text = f"다음 방: {random.choice(neighbors)}"

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
                    if event.key == pygame.K_ESCAPE:
                        return False
                    self.state = STATE_PLAYING
                elif self.state in (STATE_GAME_OVER, STATE_VICTORY):
                    if event.key == pygame.K_ESCAPE:
                        return False
                    self.restart_game()
                elif self.state == STATE_PLAYING and event.key == pygame.K_r:
                    if self.player.room_reset_charges > 0:
                        self.player.room_reset_charges -= 1
                        self.reset_room(self.current_room, first_time=True)
        return True

    def restart_game(self):
        self.state = STATE_TITLE
        self.world = WorldMap(3, self.item_library)
        self.current_room_coord = self.world.start
        self.current_room = self.world.get_room(self.current_room_coord)
        self.player = Player(ROOM_PIXEL_W // 2, ROOM_PIXEL_H // 2)
        self.floor = 1
        self.entry_text = ""
        self.hint_text = ""
        self.projectile_speed_bonus = 0
        self.enemy_speed_bonus = 0
        self.error_message = ""
        self.reset_room(self.current_room, first_time=True)

    def update(self, dt):
        if self.state != STATE_PLAYING:
            return

        keys = pygame.key.get_pressed()
        move_dir = pygame.Vector2(0, 0)
        if keys[pygame.K_w]:
            move_dir.y -= 1
        if keys[pygame.K_s]:
            move_dir.y += 1
        if keys[pygame.K_a]:
            move_dir.x -= 1
        if keys[pygame.K_d]:
            move_dir.x += 1
        self.player.move(dt, move_dir, self.current_room)

        shoot_dir = pygame.Vector2(0, 0)
        if keys[pygame.K_UP]:
            shoot_dir.y -= 1
        if keys[pygame.K_DOWN]:
            shoot_dir.y += 1
        if keys[pygame.K_LEFT]:
            shoot_dir.x -= 1
        if keys[pygame.K_RIGHT]:
            shoot_dir.x += 1
        if shoot_dir.length_squared() > 0 and self.player.can_shoot():
            projectile = Projectile(
                self.player.rect.centerx - 3,
                self.player.rect.centery - 3,
                shoot_dir,
                speed=220 + self.projectile_speed_bonus,
            )
            self.current_room.projectiles.append(projectile)
            self.player.reset_shoot()

        self.player.update(dt, self.current_room, self.player)

        for projectile in list(self.current_room.projectiles):
            projectile.update(dt, self.current_room, self.player)
            if not projectile.alive:
                self.current_room.projectiles.remove(projectile)

        for enemy in list(self.current_room.enemies):
            enemy.speed_bonus = self.enemy_speed_bonus
            enemy.update(dt, self.current_room, self.player)
            if enemy.rect.colliderect(self.player.rect):
                self.player.take_damage(1)
            if not enemy.alive:
                self.current_room.enemies.remove(enemy)

        for projectile in list(self.current_room.projectiles):
            for enemy in self.current_room.enemies:
                if projectile.rect.colliderect(enemy.rect):
                    enemy.take_damage(1)
                    projectile.alive = False
            if not projectile.alive and projectile in self.current_room.projectiles:
                self.current_room.projectiles.remove(projectile)

        for pickup in self.current_room.pickups:
            if not pickup.collected and pickup.rect.colliderect(self.player.rect):
                pickup.collected = True
                pickup.item.apply(self.player, self, self.current_room)
                self.player.item_texts.append(f"{pickup.item.name}: {pickup.item.description}")

        self.current_room.pickups = [pickup for pickup in self.current_room.pickups if not pickup.collected]

        self.current_room.update_clear_state()
        self.handle_doors()

        if self.player.hp <= 0:
            self.state = STATE_GAME_OVER

        if self.current_room_coord == (self.world.size - 1, self.world.size - 1) and self.current_room.cleared:
            self.state = STATE_VICTORY

        if self.entry_timer > 0:
            self.entry_timer -= dt

    def handle_doors(self):
        open_doors = self.get_open_doors()
        if self.current_room.cleared:
            self.current_room.rebuild_walls(list(open_doors.values()))
        else:
            self.current_room.rebuild_walls([])

        if not self.current_room.cleared:
            return

        for direction, rect in open_doors.items():
            if self.player.rect.colliderect(rect):
                self.move_room(direction)
                break

    def get_open_doors(self):
        mid_x = ROOM_PIXEL_W // 2 - TILE_SIZE // 2
        mid_y = ROOM_PIXEL_H // 2 - TILE_SIZE // 2
        doors = {
            "up": pygame.Rect(mid_x, 0, TILE_SIZE, TILE_SIZE),
            "down": pygame.Rect(mid_x, ROOM_PIXEL_H - TILE_SIZE, TILE_SIZE, TILE_SIZE),
            "left": pygame.Rect(0, mid_y, TILE_SIZE, TILE_SIZE),
            "right": pygame.Rect(ROOM_PIXEL_W - TILE_SIZE, mid_y, TILE_SIZE, TILE_SIZE),
        }
        open_doors = {}
        for direction, coord in self.world.neighbors(self.current_room_coord).items():
            if self.world.in_bounds(coord):
                open_doors[direction] = doors[direction]
        return open_doors

    def move_room(self, direction):
        next_coord = self.world.neighbors(self.current_room_coord)[direction]
        if not self.world.in_bounds(next_coord):
            return
        self.current_room_coord = next_coord
        self.current_room = self.world.get_room(self.current_room_coord)
        self.player.rect.center = (ROOM_PIXEL_W // 2, ROOM_PIXEL_H // 2)
        self.reset_room(self.current_room)

    def draw_room(self):
        floor = self.assets["floor"]
        for y in range(0, ROOM_PIXEL_H, TILE_SIZE):
            for x in range(0, ROOM_PIXEL_W, TILE_SIZE):
                self.render_surface.blit(floor, (x, y))

        wall_image = self.assets["wall"]
        for wall in self.current_room.base_walls:
            self.render_surface.blit(wall_image, wall.topleft)

        open_doors = self.get_open_doors()
        for rect in open_doors.values():
            door_image = self.assets["door_open"] if self.current_room.cleared else self.assets["door_closed"]
            self.render_surface.blit(door_image, rect.topleft)

        for px, py, prop_type in self.current_room.props:
            key = f"prop_{prop_type}"
            self.render_surface.blit(self.assets[key], (px, py))

    def draw(self):
        self.render_surface.fill((15, 15, 20))
        if self.state == STATE_TITLE:
            blink = (pygame.time.get_ticks() // 600) % 2 == 0
            self.title_renderer.draw(self.render_surface, self.big_font, self.font, blink)
        elif self.state == STATE_PLAYING:
            self.draw_room()
            for pickup in self.current_room.pickups:
                self.render_surface.blit(self.assets[pickup.item.icon_key], pickup.rect.topleft)
            for projectile in self.current_room.projectiles:
                projectile.draw(self.render_surface, self.assets["bullet"])
            for enemy in self.current_room.enemies:
                if enemy.__class__.__name__ == "Chaser":
                    enemy.draw(self.render_surface, self.assets["enemy1"])
                else:
                    enemy.draw(self.render_surface, self.assets["enemy2"])
            self.player.draw(self.render_surface, self.assets["player"])
            if self.entry_timer > 0:
                text = self.font.render(self.entry_text, True, (220, 200, 180))
                self.render_surface.blit(text, (ROOM_PIXEL_W // 2 - text.get_width() // 2, 6))
            self.hud.draw(self.render_surface, self, self.player)
        elif self.state == STATE_GAME_OVER:
            self.draw_end("게임 오버")
        elif self.state == STATE_VICTORY:
            self.draw_end("막이 내렸다")

        scaled = pygame.transform.scale(self.render_surface, self.screen.get_size())
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()

    def draw_end(self, message):
        text = self.big_font.render(message, True, (240, 120, 120))
        sub = self.font.render("ENTER로 다시", True, (180, 180, 180))
        self.render_surface.blit(text, (ROOM_PIXEL_W // 2 - text.get_width() // 2, 90))
        self.render_surface.blit(sub, (ROOM_PIXEL_W // 2 - sub.get_width() // 2, 110))

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
            self.draw()
