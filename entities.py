import random
import pygame


class Entity:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.vel = pygame.Vector2(0, 0)
        self.alive = True

    def update(self, dt, room, player):
        raise NotImplementedError

    def draw(self, surface, image):
        surface.blit(image, self.rect.topleft)


class Projectile(Entity):
    def __init__(self, x, y, direction, speed=220, lifetime=1.2):
        super().__init__(x, y, 6, 6)
        if direction.length_squared() == 0:
            direction = pygame.Vector2(1, 0)
        self.vel = pygame.Vector2(direction).normalize() * speed
        self.lifetime = lifetime

    def update(self, dt, room, player):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        self.rect.x += int(self.vel.x * dt)
        self._collide_walls(room)
        self.rect.y += int(self.vel.y * dt)
        self._collide_walls(room)

    def _collide_walls(self, room):
        for wall in room.wall_rects:
            if self.rect.colliderect(wall):
                self.alive = False
                break


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 14, 14)
        self.speed = 90
        self.max_hp = 8
        self.hp = self.max_hp
        self.shoot_cooldown = 0.22
        self.shoot_timer = 0
        self.damage_reduction = 0
        self.shield = 0
        self.room_reset_charges = 0
        self.item_texts = []
        self.damage_taken_timer = 0

    def update(self, dt, room, player):
        self.shoot_timer = max(0, self.shoot_timer - dt)
        self.damage_taken_timer = max(0, self.damage_taken_timer - dt)

    def move(self, dt, direction, room):
        if direction.length_squared() > 0:
            direction = direction.normalize()
        self.vel = direction * self.speed
        self.rect.x += int(self.vel.x * dt)
        self._collide_walls(room, axis="x")
        self.rect.y += int(self.vel.y * dt)
        self._collide_walls(room, axis="y")

    def _collide_walls(self, room, axis):
        for wall in room.wall_rects:
            if self.rect.colliderect(wall):
                if axis == "x":
                    if self.vel.x > 0:
                        self.rect.right = wall.left
                    elif self.vel.x < 0:
                        self.rect.left = wall.right
                else:
                    if self.vel.y > 0:
                        self.rect.bottom = wall.top
                    elif self.vel.y < 0:
                        self.rect.top = wall.bottom

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

    @property
    def speed(self):
        return self.base_speed + self.speed_bonus

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False


class Chaser(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=3, speed=35)

    def update(self, dt, room, player):
        direction = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        if direction.length_squared() > 0:
            direction = direction.normalize()
        self.vel = direction * self.speed
        self.rect.x += int(self.vel.x * dt)
        self._collide_walls(room, axis="x")
        self.rect.y += int(self.vel.y * dt)
        self._collide_walls(room, axis="y")

    def _collide_walls(self, room, axis):
        for wall in room.wall_rects:
            if self.rect.colliderect(wall):
                if axis == "x":
                    if self.vel.x > 0:
                        self.rect.right = wall.left
                    elif self.vel.x < 0:
                        self.rect.left = wall.right
                else:
                    if self.vel.y > 0:
                        self.rect.bottom = wall.top
                    elif self.vel.y < 0:
                        self.rect.top = wall.bottom


class Dasher(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=4, speed=20)
        self.dash_cooldown = random.uniform(1.5, 2.4)
        self.dash_timer = self.dash_cooldown
        self.dashing = False
        self.dash_duration = 0.4
        self.dash_time_left = 0
        self.dash_velocity = pygame.Vector2(0, 0)

    def update(self, dt, room, player):
        if self.dashing:
            self.dash_time_left -= dt
            if self.dash_time_left <= 0:
                self.dashing = False
                self.dash_timer = self.dash_cooldown
            self.rect.x += int(self.dash_velocity.x * dt)
            self._collide_walls(room, axis="x")
            self.rect.y += int(self.dash_velocity.y * dt)
            self._collide_walls(room, axis="y")
            return

        self.dash_timer -= dt
        direction = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        if direction.length_squared() > 0:
            direction = direction.normalize()
        self.vel = direction * self.speed
        self.rect.x += int(self.vel.x * dt)
        self._collide_walls(room, axis="x")
        self.rect.y += int(self.vel.y * dt)
        self._collide_walls(room, axis="y")

        if self.dash_timer <= 0:
            self.dashing = True
            self.dash_time_left = self.dash_duration
            self.dash_velocity = direction * (140 + self.speed_bonus)

    def _collide_walls(self, room, axis):
        for wall in room.wall_rects:
            if self.rect.colliderect(wall):
                if axis == "x":
                    if self.vel.x > 0:
                        self.rect.right = wall.left
                    elif self.vel.x < 0:
                        self.rect.left = wall.right
                    self.dashing = False
                else:
                    if self.vel.y > 0:
                        self.rect.bottom = wall.top
                    elif self.vel.y < 0:
                        self.rect.top = wall.bottom
                    self.dashing = False
