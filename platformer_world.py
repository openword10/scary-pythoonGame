import pygame

TILE_SIZE = 16
MAP_WIDTH = 80
MAP_HEIGHT = 15
LEVEL_PIXEL_W = MAP_WIDTH * TILE_SIZE
LEVEL_PIXEL_H = MAP_HEIGHT * TILE_SIZE

STAGE_LINES = [
    "컷. 다시.",
    "웃어. 장면이 망가져.",
    "관객은 없었다.",
    "대본대로 뛰어.",
]


def build_map():
    tiles = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    ground_y = MAP_HEIGHT - 2
    for x in range(MAP_WIDTH):
        tiles[ground_y][x] = 1
        tiles[ground_y + 1][x] = 1

    platforms = [
        (6, 10, 6),
        (16, 8, 5),
        (24, 11, 5),
        (33, 7, 6),
        (43, 9, 4),
        (52, 6, 7),
        (64, 10, 6),
    ]
    for start_x, y, length in platforms:
        for x in range(start_x, min(start_x + length, MAP_WIDTH - 2)):
            tiles[y][x] = 1

    holes = [(12, 2), (28, 2), (58, 3)]
    for start_x, length in holes:
        for x in range(start_x, min(start_x + length, MAP_WIDTH - 1)):
            tiles[ground_y][x] = 0
            tiles[ground_y + 1][x] = 0

    return tiles


def build_solid_rects(tiles):
    solids = []
    for y, row in enumerate(tiles):
        for x, tile in enumerate(row):
            if tile == 1:
                solids.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    return solids
