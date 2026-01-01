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
        super().__init__(x, y, 14, 16)
        self.speed = 150
        self.accel = 1300
        self.air_accel = 900
        self.friction = 1400
        self.jump_speed = 290
        self.jump_charge_max = 0.8
        self.jump_charge = 0
        self.jump_charge_rate = 1.4
        self.gravity = 900
        self.fall_gravity = 1650
        self.coyote_time = 0.1
        self.jump_buffer = 0.1
        self.coyote_timer = 0
        self.jump_buffer_timer = 0
        self.max_hp = 4
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

    def update(self, dt, world, player):
        if self.on_ground:
            self.coyote_timer = self.coyote_time
            self.can_air_dash = True
        else:
            self.coyote_timer = max(0, self.coyote_timer - dt)
        self.jump_buffer_timer = max(0, self.jump_buffer_timer - dt)
        self.attack_timer = max(0, self.attack_timer - dt)
        self.invincible_timer = max(0, self.invincible_timer - dt)
        self.dash_timer = max(0, self.dash_timer - dt)
        self.dash_time = max(0, self.dash_time - dt)
        self.dash_invincible_timer = max(0, self.dash_invincible_timer - dt)
        if not self.on_ground and abs(self.vel.y) < 15:
            self.hover_timer = self.hover_time
        else:
            self.hover_timer = max(0, self.hover_timer - dt)

    def handle_input(self, dt, keys):
        left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        accel = self.accel if self.on_ground else self.air_accel

        if left and not right:
            self.vel.x -= accel * dt
            self.vel.x = max(self.vel.x, -self.speed)
            self.facing = -1
        elif right and not left:
            self.vel.x += accel * dt
            self.vel.x = min(self.vel.x, self.speed)
            self.facing = 1
        else:
            if self.on_ground:
                if self.vel.x > 0:
                    self.vel.x = max(0, self.vel.x - self.friction * dt)
                elif self.vel.x < 0:
                    self.vel.x = min(0, self.vel.x + self.friction * dt)

        if self.on_ground and keys[pygame.K_SPACE]:
            self.jump_charge = min(self.jump_charge_max, self.jump_charge + self.jump_charge_rate * dt)

    def handle_jump_release(self):
        if self.on_ground and self.jump_charge > 0:
            boost = 1.0 + (self.jump_charge / self.jump_charge_max) * 0.6
            self.vel.y = -self.jump_speed * boost
            self.jump_charge = 0
            self.on_ground = False
            return True
        return False

    def queue_jump(self):
        self.jump_buffer_timer = self.jump_buffer

    def try_jump(self):
        if self.jump_buffer_timer > 0 and self.coyote_timer > 0:
            self.vel.y = -self.jump_speed
            self.jump_buffer_timer = 0
            self.coyote_timer = 0
            self.on_ground = False

    def try_dash(self, keys):
        if self.dash_timer > 0:
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
        offset = 16 if self.facing > 0 else -16
        rect = pygame.Rect(self.rect.centerx + offset - 12, self.rect.centery - 10, 28, 18)
        return AttackHitbox(rect)

    def take_damage(self, dmg):
        if self.invincible_timer > 0 or self.dash_invincible_timer > 0:
            return False
        self.hp = max(0, self.hp - dmg)
        self.invincible_timer = 1.0
        return True

    def should_blink(self):
        return (self.invincible_timer > 0 or self.dash_invincible_timer > 0) and int(self.invincible_timer * 10) % 2 == 0


class Enemy1(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 14, 14)
        self.speed = 55
        self.direction = -1
        self.hp = 1

    def update(self, dt, world, player):
        self.vel.x = self.direction * self.speed
        self.rect.x += int(self.vel.x * dt)
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
    def __init__(self, x, y):
        super().__init__(x, y, 14, 14)
        self.speed = 80
        self.cooldown = 1.3
        self.timer = self.cooldown
        self.dashing = False
        self.dash_time = 0
        self.direction = 1
        self.hp = 1

    def update(self, dt, world, player):
        self.timer -= dt
        if self.dashing:
            self.dash_time -= dt
            self.rect.x += int(self.speed * 2.3 * self.direction * dt)
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
            self.dash_time = 0.35


class Coin(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 12, 12)
