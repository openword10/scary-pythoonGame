import pygame

TILE_SIZE = 16
MAP_WIDTH = 90
MAP_HEIGHT = 15
LEVEL_PIXEL_W = MAP_WIDTH * TILE_SIZE
LEVEL_PIXEL_H = MAP_HEIGHT * TILE_SIZE
KILL_Y = LEVEL_PIXEL_H + 64

# 스테이지별 스폰 데이터
STAGE_SPAWNS = {
    "stage_1": {
        "boss": {"name": "director", "x": LEVEL_PIXEL_W - TILE_SIZE * 10, "y": LEVEL_PIXEL_H - TILE_SIZE * 6},
        "enemies": [
            ("enemy1", TILE_SIZE * 20, LEVEL_PIXEL_H - TILE_SIZE * 4),
            ("enemy1", TILE_SIZE * 34, LEVEL_PIXEL_H - TILE_SIZE * 4),
            ("enemy2", TILE_SIZE * 48, LEVEL_PIXEL_H - TILE_SIZE * 4),
        ],
        "hearts": [
            (TILE_SIZE * 10, LEVEL_PIXEL_H - TILE_SIZE * 6),
            (TILE_SIZE * 22, LEVEL_PIXEL_H - TILE_SIZE * 6),
            (TILE_SIZE * 40, LEVEL_PIXEL_H - TILE_SIZE * 6),
        ],
    }
}

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


class Checkpoint:
    def __init__(self, x, y, label="체크포인트"):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE * 2)
        self.label = label


def build_map():
    # 기본 지형/플랫폼/구멍 생성
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


def build_checkpoints():
    return [
        Checkpoint(TILE_SIZE * 20, LEVEL_PIXEL_H - TILE_SIZE * 4),
        Checkpoint(TILE_SIZE * 50, LEVEL_PIXEL_H - TILE_SIZE * 4),
        Checkpoint(TILE_SIZE * 72, LEVEL_PIXEL_H - TILE_SIZE * 4),
    ]
