import random
import pygame

from entities import Chaser, Dasher
from items import ItemPickup

TILE_SIZE = 16
ROOM_TILES_W = 20
ROOM_TILES_H = 15
ROOM_PIXEL_W = ROOM_TILES_W * TILE_SIZE
ROOM_PIXEL_H = ROOM_TILES_H * TILE_SIZE

ENTRY_LINES = [
    "컷. 다시.",
    "웃어. 장면이 망가져.",
    "관객은 없었다.",
    "대본대로 움직여.",
]


class Room:
    def __init__(self, coord, item_library):
        self.coord = coord
        self.item_library = item_library
        self.enemies = []
        self.projectiles = []
        self.pickups = []
        self.props = []
        self.cleared = False
        self.visited = False
        self.message = ""
        self.base_walls = []
        self.wall_rects = []
        self._build_room()

    def _build_room(self):
        # 방 기본 벽 구성
        self.base_walls = []
        for x in range(ROOM_TILES_W):
            self.base_walls.append(pygame.Rect(x * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))
            self.base_walls.append(
                pygame.Rect(x * TILE_SIZE, (ROOM_TILES_H - 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            )
        for y in range(1, ROOM_TILES_H - 1):
            self.base_walls.append(pygame.Rect(0, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            self.base_walls.append(
                pygame.Rect((ROOM_TILES_W - 1) * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            )
        self._build_props()

    def _build_props(self):
        self.props = []
        for _ in range(random.randint(5, 9)):
            px = random.randint(2, ROOM_TILES_W - 3) * TILE_SIZE
            py = random.randint(2, ROOM_TILES_H - 3) * TILE_SIZE
            prop_type = random.choice(["tape", "mark", "curtain"])
            self.props.append((px, py, prop_type))

    def rebuild_walls(self, open_doors):
        self.wall_rects = list(self.base_walls)
        for door_rect in open_doors:
            self.wall_rects = [wall for wall in self.wall_rects if not wall.colliderect(door_rect)]

    def spawn_enemies(self, difficulty):
        # 난이도에 따른 적 생성
        self.enemies = []
        count = random.randint(2, 4 + difficulty)
        for _ in range(count):
            x = random.randint(3, ROOM_TILES_W - 4) * TILE_SIZE
            y = random.randint(3, ROOM_TILES_H - 4) * TILE_SIZE
            if random.random() < 0.55:
                self.enemies.append(Chaser(x, y))
            else:
                self.enemies.append(Dasher(x, y))

    def spawn_item(self):
        item = self.item_library.random_item()
        x = ROOM_PIXEL_W // 2 - 8
        y = ROOM_PIXEL_H // 2 - 8
        self.pickups.append(ItemPickup(x, y, item))

    def update_clear_state(self):
        if not self.cleared and all(not enemy.alive for enemy in self.enemies):
            self.cleared = True
            if not self.pickups:
                self.spawn_item()


class WorldMap:
    def __init__(self, size, item_library):
        # 지정된 크기의 월드맵 생성
        self.size = size
        self.item_library = item_library
        self.rooms = {}
        for y in range(size):
            for x in range(size):
                self.rooms[(x, y)] = Room((x, y), item_library)
        self.start = (size // 2, size // 2)

    def get_room(self, coord):
        return self.rooms.get(coord)

    def neighbors(self, coord):
        x, y = coord
        return {
            "up": (x, y - 1),
            "down": (x, y + 1),
            "left": (x - 1, y),
            "right": (x + 1, y),
        }

    def in_bounds(self, coord):
        x, y = coord
        return 0 <= x < self.size and 0 <= y < self.size
