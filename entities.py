import math
import random
import pygame


class Entity:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.vel = pygame.Vector2(0, 0)
        self.alive = True

    def update(self, dt, world, player):
        raise NotImplementedError


class AttackHitbox:
    def __init__(self, rect, duration=0.12):
        self.rect = rect
        self.timer = duration
        self.active = True

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.active = False


class Particle:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(random.uniform(-90, 90), random.uniform(-160, -50))
        self.timer = random.uniform(0.4, 0.8)

    def update(self, dt):
        self.timer -= dt
        self.vel.y += 450 * dt
        self.pos += self.vel * dt

    def alive(self):
        return self.timer > 0


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 18, 24)
        self.base_speed = 140
        self.run_speed = 200
        self.accel = 1400
        self.air_accel = 1000
        self.friction = 1600
        self.jump_speed = 280
        self.jump_charge_max = 0.7
        self.jump_charge = 0
        self.jump_charge_rate = 2.0
        self.jump_charge_full = False
        self.gravity = 900
        self.fall_gravity = 1700
        self.coyote_time = 0.12
        self.jump_buffer = 0.12
        self.coyote_timer = 0
        self.jump_buffer_timer = 0
        self.max_hp = 5
        self.hp = self.max_hp
        self.on_ground = False
        self.score = 0
        self.facing = 1
        self.attack_cooldown = 0.3
        self.attack_timer = 0
        self.invincible_timer = 0
        self.dash_cooldown = 0.7
        self.dash_timer = 0
        self.dash_speed = 320
        self.dash_time = 0
        self.dash_invincible_timer = 0
        self.hover_time = 0.08
        self.hover_timer = 0
        self.can_air_dash = True
        self.charging_jump = False
        self.anim_timer = 0

    def update(self, dt, world, player):
        if self.on_ground:
            self.coyote_timer = self.coyote_time
            self.can_air_dash = True
            self.jumps_remaining = self.max_jumps
        else:
            self.coyote_timer = max(0, self.coyote_timer - dt)
        self.attack_timer = max(0, self.attack_timer - dt)
        self.invincible_timer = max(0, self.invincible_timer - dt)
        self.dash_timer = max(0, self.dash_timer - dt)
        self.dash_time = max(0, self.dash_time - dt)
        self.dash_invincible_timer = max(0, self.dash_invincible_timer - dt)
        if not self.on_ground and abs(self.vel.y) < 15:
            self.hover_timer = self.hover_time
        else:
            self.hover_timer = max(0, self.hover_timer - dt)
        if abs(self.vel.x) > 10 and self.on_ground:
            self.anim_timer += dt
        else:
            self.anim_timer = 0

    def handle_input(self, dt, keys):
        left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        accel = self.accel if self.on_ground else self.air_accel
        speed = self.run_speed if running else self.base_speed

        if left and not right:
            self.vel.x -= accel * dt
            self.vel.x = max(self.vel.x, -speed)
            self.facing = -1
        elif right and not left:
            self.vel.x += accel * dt
            self.vel.x = min(self.vel.x, speed)
            self.facing = 1
        else:
            if self.on_ground:
                if self.vel.x > 0:
                    self.vel.x = max(0, self.vel.x - self.friction * dt)
                elif self.vel.x < 0:
                    self.vel.x = min(0, self.vel.x + self.friction * dt)

        if self.on_ground and not self.charging_jump and keys[pygame.K_SPACE]:
            self.charging_jump = True
            self.jump_charge = 0
            self.jump_charge_full = False
        if self.on_ground and self.charging_jump:
            self.jump_charge = min(self.jump_charge_max, self.jump_charge + self.jump_charge_rate * dt)
            self.jump_charge_full = self.jump_charge >= self.jump_charge_max
        if not self.charging_jump:
            self.jump_charge_full = False

    def start_jump_charge(self):
        if self.on_ground:
            self.charging_jump = True
            self.jump_charge = 0
            self.jump_charge_full = False
            return True
        return False

    def handle_jump_release(self):
        if self.charging_jump and (self.on_ground or self.coyote_timer > 0):
            ratio = max(0.0, self.jump_charge / self.jump_charge_max)
            if ratio < 0.05:
                boost = 1.0
            else:
                boost = 1.0 + ratio * 0.3
            self.vel.y = -self.jump_speed * boost
            self.jump_charge = 0
            self.jump_charge_full = False
            self.charging_jump = False
            self.on_ground = False
            self.coyote_timer = 0
            return True
        self.charging_jump = False
        self.jump_charge = 0
        self.jump_charge_full = False
        return False

    def queue_jump(self):
        self.jump_buffer_timer = self.jump_buffer

    def try_jump(self):
        if self.jump_buffer_timer > 0 and self.coyote_timer > 0 and not self.charging_jump:
            self.vel.y = -self.jump_speed
            self.jump_buffer_timer = 0
            self.coyote_timer = 0
            self.on_ground = False

    def try_dash(self, keys):
        if self.dash_timer > 0 or self.dash_time > 0:
            return
        if not (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            return
        if not self.can_air_dash:
            return
        direction = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction = 1
        if direction != 0:
            self.vel.x = direction * self.dash_speed
            self.dash_time = 0.14
            self.dash_timer = self.dash_cooldown
            self.dash_invincible_timer = 0.2
            self.can_air_dash = False

    def apply_gravity(self, dt, jump_held):
        if self.dash_time > 0:
            return
        if self.hover_timer > 0 and self.vel.y > 0:
            self.vel.y += self.gravity * 0.3 * dt
        else:
            gravity = self.gravity if self.vel.y < 0 and jump_held else self.fall_gravity
            self.vel.y += gravity * dt

    def move_and_collide(self, dt, solids):
        self.rect.x += int(self.vel.x * dt)
        self._collide_axis(solids, axis="x")
        self.rect.y += int(self.vel.y * dt)
        self.on_ground = False
        self._collide_axis(solids, axis="y")

    def _collide_axis(self, solids, axis):
        for solid in solids:
            if self.rect.colliderect(solid):
                if axis == "x":
                    if self.vel.x > 0:
                        self.rect.right = solid.left
                    elif self.vel.x < 0:
                        self.rect.left = solid.right
                    self.vel.x = 0
                else:
                    if self.vel.y > 0:
                        self.rect.bottom = solid.top
                        self.on_ground = True
                    elif self.vel.y < 0:
                        self.rect.top = solid.bottom
                    self.vel.y = 0

    def can_attack(self):
        return self.attack_timer <= 0

    def create_attack_hitbox(self):
        if not self.can_attack():
            return None
        self.attack_timer = self.attack_cooldown
        offset = 18 if self.facing > 0 else -18
        rect = pygame.Rect(self.rect.centerx + offset - 12, self.rect.centery - 10, 30, 18)
        return AttackHitbox(rect)

    def take_damage(self, dmg):
        if self.invincible_timer > 0 or self.dash_invincible_timer > 0:
            return False
        self.hp = max(0, self.hp - dmg)
        self.invincible_timer = 0.5
        return True

    def should_blink(self):
        return (self.invincible_timer > 0 or self.dash_invincible_timer > 0) and int(self.invincible_timer * 10) % 2 == 0


class Enemy1(Entity):
    def __init__(self, x, y, speed=55):
        super().__init__(x, y, 14, 14)
        self.speed = speed
        self.direction = -1
        self.hp = 1
        self.anim_timer = 0

    def update(self, dt, world, player):
        self.vel.x = self.direction * self.speed
        self.rect.x += int(self.vel.x * dt)
        if abs(self.vel.x) > 1:
            self.anim_timer += dt
        else:
            self.anim_timer = 0
        hit_wall = False
        for solid in world.solids:
            if self.rect.colliderect(solid):
                hit_wall = True
                if self.vel.x > 0:
                    self.rect.right = solid.left
                elif self.vel.x < 0:
                    self.rect.left = solid.right
        if hit_wall:
            self.direction *= -1
            return
        front_x = self.rect.centerx + self.direction * 8
        front_y = self.rect.bottom + 1
        if not world.is_solid_at(front_x, front_y):
            self.direction *= -1


class Enemy2(Entity):
    def __init__(self, x, y, speed=80):
        super().__init__(x, y, 14, 14)
        self.speed = speed
        self.cooldown = 1.2
        self.timer = self.cooldown
        self.dashing = False
        self.dash_time = 0
        self.direction = 1
        self.hp = 1
        self.anim_timer = 0
        self.base_y = y
        self.float_timer = random.uniform(0, 1)

    def update(self, dt, world, player):
        self.timer -= dt
        self.float_timer += dt
        self.rect.y = self.base_y + int(2 * math.sin(self.float_timer * 3))
        self.anim_timer += dt
        if self.dashing:
            self.dash_time -= dt
            self.rect.x += int(self.speed * 2.4 * self.direction * dt)
            for solid in world.solids:
                if self.rect.colliderect(solid):
                    if self.direction > 0:
                        self.rect.right = solid.left
                    else:
                        self.rect.left = solid.right
                    self.dashing = False
                    self.timer = self.cooldown
            if self.dash_time <= 0:
                self.dashing = False
                self.timer = self.cooldown
            return

        if self.timer <= 0:
            self.direction = 1 if player.rect.centerx > self.rect.centerx else -1
            self.dashing = True
            self.dash_time = 0.32


class Heart(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 12, 12)
        self.float_timer = random.uniform(0, 1)
        self.base_y = y

    def update(self, dt, world, player):
        self.float_timer += dt
        self.rect.y = self.base_y + int(2 * math.sin(self.float_timer * 3))


class BossAttack:
    def __init__(self, rect, duration=0.35, damage=1, color=(220, 80, 80)):
        self.rect = rect
        self.timer = duration
        self.damage = damage
        self.color = color
        self.active = True

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.active = False


class BossTelegraph:
    def __init__(self, rect, duration=0.4, color=(220, 200, 80)):
        self.rect = rect
        self.timer = duration
        self.active = True
        self.color = color

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.active = False


class BossBase(Entity):
    def __init__(self, x, y, width, height, hp):
        super().__init__(x, y, width, height)
        self.max_hp = hp
        self.hp = hp
        self.phase = 1
        self.state = "idle"
        self.state_timer = 0
        self.attack_timer = 0
        self.attacks = []
        self.telegraphs = []
        self.color = (160, 160, 180)

    def update(self, dt, world, player):
        self.state_timer = max(0, self.state_timer - dt)
        for attack in list(self.attacks):
            attack.update(dt)
            if not attack.active:
                self.attacks.remove(attack)
        for telegraph in list(self.telegraphs):
            telegraph.update(dt)
            if not telegraph.active:
                self.telegraphs.remove(telegraph)

    def spawn_telegraph(self, rect, duration=0.4, color=(220, 200, 80)):
        self.telegraphs.append(BossTelegraph(rect, duration, color))

    def spawn_attack(self, rect, duration=0.35, damage=1, color=(220, 80, 80)):
        self.attacks.append(BossAttack(rect, duration, damage, color))

    def apply_damage(self, dmg):
        self.hp = max(0, self.hp - dmg)
        if self.hp == 0:
            self.alive = False


class DirectorBoss(BossBase):
    def __init__(self, x, y):
        super().__init__(x, y, 32, 40, hp=20)
        self.color = (140, 110, 160)

    def update(self, dt, world, player):
        super().update(dt, world, player)
        hp_ratio = self.hp / self.max_hp
        self.phase = 1 if hp_ratio > 0.7 else 2 if hp_ratio > 0.3 else 3
        self.attack_timer -= dt
        if self.attack_timer > 0:
            return

        if self.phase == 1:
            self._camera_beam(player, world)
            self.attack_timer = 1.6
        elif self.phase == 2:
            if random.random() < 0.5:
                self._spotlight(world)
            else:
                self._camera_beam(player, world)
            self.attack_timer = 1.3
        else:
            roll = random.random()
            if roll < 0.4:
                self._camera_beam(player, world)
            elif roll < 0.8:
                self._spotlight(world)
            else:
                self._cut_command(player)
            self.attack_timer = 1.1

    def _camera_beam(self, player, world):
        rect = pygame.Rect(world.camera_x if hasattr(world, "camera_x") else 0, player.rect.centery - 6, world.level_width, 12)
        self.spawn_telegraph(rect, duration=0.4, color=(220, 120, 120))
        self.spawn_attack(rect, duration=0.3, damage=2)

    def _spotlight(self, world):
        x = self.rect.centerx + random.randint(-80, 80)
        y = self.rect.bottom + 20
        rect = pygame.Rect(x - 18, y - 18, 36, 36)
        self.spawn_telegraph(rect, duration=0.5, color=(220, 200, 100))
        self.spawn_attack(rect, duration=0.35, damage=2, color=(220, 120, 80))

    def _cut_command(self, player):
        rect = pygame.Rect(player.rect.centerx - 10, player.rect.centery - 10, 20, 20)
        self.spawn_telegraph(rect, duration=0.3, color=(200, 200, 200))
        self.spawn_attack(rect, duration=0.2, damage=1, color=(200, 200, 220))


class DancerBoss(BossBase):
    def __init__(self, x, y):
        super().__init__(x, y, 26, 38, hp=18)
        self.color = (180, 80, 110)

    def update(self, dt, world, player):
        super().update(dt, world, player)
        hp_ratio = self.hp / self.max_hp
        self.phase = 1 if hp_ratio > 0.7 else 2 if hp_ratio > 0.3 else 3
        self.attack_timer -= dt
        if self.attack_timer > 0:
            return

        if self.phase == 1:
            self._ribbon_slash(player)
            self.attack_timer = 1.3
        elif self.phase == 2:
            if random.random() < 0.5:
                self._dive_stab(player)
            else:
                self._ribbon_slash(player)
            self.attack_timer = 1.1
        else:
            roll = random.random()
            if roll < 0.4:
                self._afterimage_fake(player)
            elif roll < 0.7:
                self._dive_stab(player)
            else:
                self._ribbon_slash(player)
            self.attack_timer = 0.95

    def _ribbon_slash(self, player):
        direction = 1 if player.rect.centerx >= self.rect.centerx else -1
        rect = pygame.Rect(self.rect.centerx + direction * 10, self.rect.centery - 12, 36, 24)
        self.spawn_telegraph(rect, duration=0.3, color=(220, 150, 180))
        self.spawn_attack(rect, duration=0.3, damage=2, color=(200, 80, 120))

    def _dive_stab(self, player):
        rect = pygame.Rect(player.rect.centerx - 12, player.rect.centery - 24, 24, 48)
        self.spawn_telegraph(rect, duration=0.35, color=(200, 200, 220))
        self.spawn_attack(rect, duration=0.25, damage=2, color=(160, 120, 220))

    def _afterimage_fake(self, player):
        rect = pygame.Rect(player.rect.centerx - 18, player.rect.centery - 12, 36, 24)
        self.spawn_telegraph(rect, duration=0.2, color=(140, 140, 180))
        self.spawn_attack(rect, duration=0.2, damage=2, color=(200, 80, 100))


class JudgeBoss(BossBase):
    def __init__(self, x, y):
        super().__init__(x, y, 36, 44, hp=22)
        self.color = (110, 140, 180)

    def update(self, dt, world, player):
        super().update(dt, world, player)
        hp_ratio = self.hp / self.max_hp
        self.phase = 1 if hp_ratio > 0.7 else 2 if hp_ratio > 0.3 else 3
        self.attack_timer -= dt
        if self.attack_timer > 0:
            return

        if self.phase == 1:
            self._hammer_drop(player)
            self.attack_timer = 1.5
        elif self.phase == 2:
            if random.random() < 0.5:
                self._scale_verdict(player)
            else:
                self._hammer_drop(player)
            self.attack_timer = 1.3
        else:
            roll = random.random()
            if roll < 0.4:
                self._scale_verdict(player)
            elif roll < 0.8:
                self._judgement_zone(player)
            else:
                self._hammer_drop(player)
            self.attack_timer = 1.1

    def _hammer_drop(self, player):
        rect = pygame.Rect(player.rect.centerx - 16, player.rect.centery - 20, 32, 40)
        self.spawn_telegraph(rect, duration=0.6, color=(200, 180, 120))
        self.spawn_attack(rect, duration=0.3, damage=2, color=(180, 120, 80))

    def _scale_verdict(self, player):
        left_rect = pygame.Rect(player.rect.centerx - 70, player.rect.centery - 16, 40, 32)
        right_rect = pygame.Rect(player.rect.centerx + 30, player.rect.centery - 16, 40, 32)
        danger = left_rect if random.random() < 0.5 else right_rect
        self.spawn_telegraph(danger, duration=0.45, color=(200, 120, 120))
        self.spawn_attack(danger, duration=0.35, damage=2, color=(160, 80, 80))

    def _judgement_zone(self, player):
        rect = pygame.Rect(player.rect.centerx - 50, player.rect.centery - 10, 100, 20)
        self.spawn_telegraph(rect, duration=0.4, color=(180, 200, 200))
        self.spawn_attack(rect, duration=0.5, damage=1, color=(140, 180, 180))


class ClownBoss(BossBase):
    def __init__(self, x, y):
        super().__init__(x, y, 30, 36, hp=19)
        self.color = (200, 120, 80)

    def update(self, dt, world, player):
        super().update(dt, world, player)
        hp_ratio = self.hp / self.max_hp
        self.phase = 1 if hp_ratio > 0.7 else 2 if hp_ratio > 0.3 else 3
        self.attack_timer -= dt
        if self.attack_timer > 0:
            return

        if self.phase == 1:
            self._flip_charge(player)
            self.attack_timer = 1.4
        elif self.phase == 2:
            if random.random() < 0.5:
                self._clone_slash(player)
            else:
                self._flip_charge(player)
            self.attack_timer = 1.2
        else:
            roll = random.random()
            if roll < 0.4:
                self._wire_mandate(player)
            elif roll < 0.8:
                self._clone_slash(player)
            else:
                self._flip_charge(player)
            self.attack_timer = 1.0

    def _flip_charge(self, player):
        rect = pygame.Rect(player.rect.centerx - 30, player.rect.centery - 10, 60, 20)
        self.spawn_telegraph(rect, duration=0.4, color=(200, 140, 80))
        self.spawn_attack(rect, duration=0.3, damage=2, color=(200, 90, 60))

    def _clone_slash(self, player):
        rect = pygame.Rect(player.rect.centerx - 20, player.rect.centery - 20, 40, 40)
        self.spawn_telegraph(rect, duration=0.35, color=(140, 140, 140))
        self.spawn_attack(rect, duration=0.3, damage=2, color=(180, 60, 60))

    def _wire_mandate(self, player):
        rect = pygame.Rect(player.rect.centerx - 80, player.rect.centery - 6, 160, 12)
        self.spawn_telegraph(rect, duration=0.4, color=(220, 100, 100))
        self.spawn_attack(rect, duration=0.35, damage=2, color=(200, 60, 80))


class ArchivistBoss(BossBase):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 46, hp=24)
        self.color = (100, 140, 120)

    def update(self, dt, world, player):
        super().update(dt, world, player)
        hp_ratio = self.hp / self.max_hp
        self.phase = 1 if hp_ratio > 0.7 else 2 if hp_ratio > 0.3 else 3
        self.attack_timer -= dt
        if self.attack_timer > 0:
            return

        if self.phase == 1:
            self._page_storm(player)
            self.attack_timer = 1.6
        elif self.phase == 2:
            if random.random() < 0.5:
                self._shelf_press(player)
            else:
                self._page_storm(player)
            self.attack_timer = 1.3
        else:
            roll = random.random()
            if roll < 0.4:
                self._time_stasis(player)
            elif roll < 0.8:
                self._shelf_press(player)
            else:
                self._page_storm(player)
            self.attack_timer = 1.1

    def _page_storm(self, player):
        rect = pygame.Rect(player.rect.centerx - 60, player.rect.centery - 16, 120, 32)
        self.spawn_telegraph(rect, duration=0.35, color=(160, 200, 160))
        self.spawn_attack(rect, duration=0.4, damage=2, color=(120, 160, 120))

    def _shelf_press(self, player):
        rect = pygame.Rect(player.rect.centerx - 90, player.rect.centery - 24, 180, 48)
        self.spawn_telegraph(rect, duration=0.45, color=(160, 120, 80))
        self.spawn_attack(rect, duration=0.35, damage=2, color=(120, 90, 60))

    def _time_stasis(self, player):
        rect = pygame.Rect(player.rect.centerx - 30, player.rect.centery - 30, 60, 60)
        self.spawn_telegraph(rect, duration=0.4, color=(140, 180, 220))
        self.spawn_attack(rect, duration=0.3, damage=1, color=(100, 140, 200))
