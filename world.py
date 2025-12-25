import random
import pygame

from entities import Chaser, Dasher
from items import ItemPickup


TILE_SIZE = 16
VIEW_TILES_W = 30
VIEW_TILES_H = 17
VIEW_PIXEL_W = VIEW_TILES_W * TILE_SIZE
VIEW_PIXEL_H = VIEW_TILES_H * TILE_SIZE
LEVEL_TILES_W = 120
LEVEL_TILES_H = 20
LEVEL_PIXEL_W = LEVEL_TILES_W * TILE_SIZE
LEVEL_PIXEL_H = LEVEL_TILES_H * TILE_SIZE



class Level:
    def __init__(self, item_library):
        self.item_library = item_library
        self.tiles = []
        self.solid_rects = []
        self.enemies = []
        self.projectiles = []
        self.pickups = []
        self.props = []
        self.exit_rect = pygame.Rect(LEVEL_PIXEL_W - TILE_SIZE * 2, TILE_SIZE * 2, TILE_SIZE, TILE_SIZE * 3)
        self._build_tiles()
        self._build_props()
        self._spawn_enemies()
        self._spawn_items()

    def _build_tiles(self):
        self.tiles = [[0 for _ in range(LEVEL_TILES_W)] for _ in range(LEVEL_TILES_H)]
        ground_y = LEVEL_TILES_H - 2
        for x in range(LEVEL_TILES_W):
            self.tiles[ground_y][x] = 1
            self.tiles[ground_y + 1][x] = 1

        platform_specs = [
            (6, 13, 6),
            (18, 11, 8),
            (34, 14, 5),
            (46, 10, 7),
            (60, 12, 6),
            (75, 9, 10),
            (92, 13, 8),
            (108, 11, 6),
        ]
        for start_x, y, length in platform_specs:
            for x in range(start_x, min(start_x + length, LEVEL_TILES_W - 2)):
                self.tiles[y][x] = 1

        self._rebuild_solids()

    def _rebuild_solids(self):
        self.solid_rects = []
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                if tile == 1:
                    self.solid_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    def _build_props(self):
        self.props = []
        for _ in range(32):
            px = random.randint(2, LEVEL_TILES_W - 3) * TILE_SIZE
            py = random.randint(2, LEVEL_TILES_H - 5) * TILE_SIZE
            prop_type = random.choice(["tape", "mark", "curtain"])
            self.props.append((px, py, prop_type))

    def _spawn_enemies(self):
        self.enemies = []
        spawn_points = [
            (10, 15),
            (24, 10),
            (30, 15),
            (52, 9),
            (66, 11),
            (80, 8),
            (96, 14),
            (110, 10),
        ]
        for idx, (x, y) in enumerate(spawn_points):
            px = x * TILE_SIZE
            py = y * TILE_SIZE
            if idx % 2 == 0:
                self.enemies.append(Chaser(px, py))
            else:
                self.enemies.append(Dasher(px, py))

    def _spawn_items(self):
        self.pickups = []
        for x in (14, 40, 70, 100):
            item = self.item_library.random_item()
            self.pickups.append(ItemPickup(x * TILE_SIZE, (LEVEL_TILES_H - 4) * TILE_SIZE, item))

    def update_clear_state(self):
        return all(not enemy.alive for enemy in self.enemies)
WorldMap = Level
ROOM_PIXEL_W = VIEW_PIXEL_W
ROOM_PIXEL_H = VIEW_PIXEL_H