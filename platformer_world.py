import pygame

TILE_SIZE = 16
MAP_WIDTH = 90
MAP_HEIGHT = 15
LEVEL_PIXEL_W = MAP_WIDTH * TILE_SIZE
LEVEL_PIXEL_H = MAP_HEIGHT * TILE_SIZE
KILL_Y = LEVEL_PIXEL_H + 64

STAGE_LINES = [
    "컷. 다시.",
    "웃어. 장면이 망가져.",
    "관객은 없었다.",
    "대본대로 뛰어.",
    "임무는 끝나지 않았다.",
]


class Sign:
    def __init__(self, x, y, text):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.text = text


def build_map():
    tiles = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    ground_y = MAP_HEIGHT - 2
    for x in range(MAP_WIDTH):
        tiles[ground_y][x] = 1
        tiles[ground_y + 1][x] = 1

    platforms = [
        (6, 10, 7),
        (18, 9, 6),
        (28, 11, 6),
        (40, 8, 7),
        (52, 9, 6),
        (64, 7, 8),
        (76, 10, 8),
        (82, 8, 6),
        (84, 6, 4),
    ]
    for start_x, y, length in platforms:
        for x in range(start_x, min(start_x + length, MAP_WIDTH - 2)):
            tiles[y][x] = 1

    holes = [(14, 2), (34, 3), (58, 3)]
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


def build_signs():
    return [
        Sign(TILE_SIZE * 8, LEVEL_PIXEL_H - TILE_SIZE * 4, "대본은 거짓을 말하라 했다."),
        Sign(TILE_SIZE * 30, LEVEL_PIXEL_H - TILE_SIZE * 4, "커튼 뒤엔 아무도 없었다."),
        Sign(TILE_SIZE * 54, LEVEL_PIXEL_H - TILE_SIZE * 4, "임무는 복수였다."),
        Sign(TILE_SIZE * 74, LEVEL_PIXEL_H - TILE_SIZE * 4, "가짜를 진짜로 믿게 됐다."),
    ]
