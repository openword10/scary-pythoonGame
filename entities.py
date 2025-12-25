import random
import pygame


class Entity:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.vel = pygame.Vector2(0, 0)
        self.alive = True

    def update(self, dt, level, player):
        raise NotImplementedError

    def draw(self, surface, image, offset):
        surface.blit(image, (self.rect.x - offset.x, self.rect.y - offset.y))


class Projectile(Entity):
    def __init__(self, x, y, direction, speed=260, lifetime=1.2):
        super().__init__(x, y, 6, 6)
        if direction.length_squared() == 0:
            direction = pygame.Vector2(1, 0)
        self.vel = pygame.Vector2(direction).normalize() * speed
        self.lifetime = lifetime

    def update(self, dt, level, player):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        self.rect.x += int(self.vel.x * dt)
        self._collide_solids(level)
        self.rect.y += int(self.vel.y * dt)
        self._collide_solids(level)

    def _collide_solids(self, level):
        for solid in level.solid_rects:
            if self.rect.colliderect(solid):
                self.alive = False
                break


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 14, 16)
        self.speed = 110
        self.jump_power = 220
        self.gravity = 520
        self.max_hp = 8
        self.hp = self.max_hp
        self.shoot_cooldown = 0.25
        self.shoot_timer = 0
        self.damage_reduction = 0
        self.shield = 0
        self.room_reset_charges = 0
        self.item_texts = []
        self.damage_taken_timer = 0
        self.on_ground = False
        self.facing = 1

    def update(self, dt, level, player):
        self.shoot_timer = max(0, self.shoot_timer - dt)
        self.damage_taken_timer = max(0, self.damage_taken_timer - dt)

    def move(self, dt, direction, level):
        if direction.x != 0:
            self.facing = 1 if direction.x > 0 else -1
        self.vel.x = direction.x * self.speed
        self.rect.x += int(self.vel.x * dt)
        self._collide_solids(level, axis="x")

        self.vel.y += self.gravity * dt
        self.rect.y += int(self.vel.y * dt)
        self.on_ground = False
        self._collide_solids(level, axis="y")

    def jump(self):
        if self.on_ground:
            self.vel.y = -self.jump_power
            self.on_ground = False

    def _collide_solids(self, level, axis):
        for solid in level.solid_rects:
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

    def take_damage(self, amount):
        if self.damage_taken_timer > 0:
            return
        if self.shield > 0:
            self.shield -= 1
            self.damage_taken_timer = 0.6
            return
        damage = max(1, amount - self.damage_reduction)
        self.hp = max(0, self.hp - damage)
        self.damage_taken_timer = 0.6

    def can_shoot(self):
        return self.shoot_timer <= 0

    def reset_shoot(self):
        self.shoot_timer = self.shoot_cooldown


class Enemy(Entity):
    def __init__(self, x, y, hp=3, speed=40):
        super().__init__(x, y, 14, 14)
        self.hp = hp
        self.base_speed = speed
        self.speed_bonus = 0
        self.gravity = 520
        self.on_ground = False

    @property
    def speed(self):
        return self.base_speed + self.speed_bonus

    def apply_gravity(self, dt, level):
        self.vel.y += self.gravity * dt
        self.rect.y += int(self.vel.y * dt)
        self.on_ground = False
        for solid in level.solid_rects:
            if self.rect.colliderect(solid):
                if self.vel.y > 0:
                    self.rect.bottom = solid.top
                    self.on_ground = True
                elif self.vel.y < 0:
                    self.rect.top = solid.bottom
                self.vel.y = 0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False


class Chaser(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=3, speed=40)

    def update(self, dt, level, player):
        direction = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        if abs(direction.x) > 4:
            direction.x = 1 if direction.x > 0 else -1
        else:
            direction.x = 0
        self.vel.x = direction.x * self.speed
        self.rect.x += int(self.vel.x * dt)
        self._collide_solids(level)
        self.apply_gravity(dt, level)

    def _collide_solids(self, level):
        for solid in level.solid_rects:
            if self.rect.colliderect(solid):
                if self.vel.x > 0:
                    self.rect.right = solid.left
                elif self.vel.x < 0:
                    self.rect.left = solid.right
                self.vel.x = 0


class Dasher(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=4, speed=30)
        self.dash_cooldown = random.uniform(1.3, 2.2)
        self.dash_timer = self.dash_cooldown
        self.dashing = False
        self.dash_duration = 0.4
        self.dash_time_left = 0
        self.dash_velocity = 0

    def update(self, dt, level, player):
        if self.dashing:
            self.dash_time_left -= dt
            if self.dash_time_left <= 0:
                self.dashing = False
                self.dash_timer = self.dash_cooldown
            self.rect.x += int(self.dash_velocity * dt)
            self._collide_solids(level)
            self.apply_gravity(dt, level)
            return

        self.dash_timer -= dt
        direction = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        if abs(direction.x) > 6:
            direction.x = 1 if direction.x > 0 else -1
        else:
            direction.x = 0
        self.vel.x = direction.x * self.speed
        self.rect.x += int(self.vel.x * dt)
        self._collide_solids(level)
        self.apply_gravity(dt, level)

        if self.dash_timer <= 0 and direction.x != 0:
            self.dashing = True
            self.dash_time_left = self.dash_duration
            self.dash_velocity = direction.x * (150 + self.speed_bonus)

    def _collide_solids(self, level):
        for solid in level.solid_rects:
            if self.rect.colliderect(solid):
                if self.vel.x > 0:
                    self.rect.right = solid.left
                elif self.vel.x < 0:
                    self.rect.left = solid.right
                self.vel.x = 0
                self.dashing = False
