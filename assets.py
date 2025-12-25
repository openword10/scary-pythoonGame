import os
import random
import pygame

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

PLAYER_NAME = "주인공"
ENEMY1_NAME = "괴물1"
ENEMY2_NAME = "괴물2"

ASSET_FILES = {
    "player": "player.png",
    "enemy1": "enemy1.png",
    "enemy2": "enemy2.png",
    "bullet": "bullet.png",
    "floor": "floor.png",
    "wall": "wall.png",
    "door_closed": "door_closed.png",
    "door_open": "door_open.png",
    "prop_tape": "prop_tape.png",
    "prop_mark": "prop_mark.png",
    "prop_curtain": "prop_curtain.png",
    "item_mask": "item_mask.png",
    "item_tape": "item_tape.png",
    "item_script": "item_script.png",
    "item_spotlight": "item_spotlight.png",
    "item_eraser": "item_eraser.png",
    "item_scissors": "item_scissors.png",
}


def _safe_print(message):
    try:
        print(message)
    except Exception:
        pass


def _ensure_dir():
    try:
        os.makedirs(ASSET_DIR, exist_ok=True)
    except Exception as exc:
        _safe_print(f"[assets] 폴더 생성 실패: {exc}")


def _save_surface(surface, filename):
    path = os.path.join(ASSET_DIR, filename)
    try:
        pygame.image.save(surface, path)
    except Exception as exc:
        _safe_print(f"[assets] 저장 실패: {path} ({exc})")


def _draw_pixel(surface, x, y, color):
    if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
        surface.set_at((x, y), color)


def _create_player():
    surface = pygame.Surface((16, 16), pygame.SRCALPHA)
    surface.fill((40, 40, 60))
    for x in range(4, 12):
        for y in range(3, 13):
            _draw_pixel(surface, x, y, (210, 210, 220))
    _draw_pixel(surface, 6, 7, (30, 30, 40))
    _draw_pixel(surface, 9, 7, (30, 30, 40))
    _draw_pixel(surface, 7, 10, (120, 80, 80))
    _draw_pixel(surface, 8, 10, (120, 80, 80))
    return surface


def _create_enemy1():
    surface = pygame.Surface((16, 16), pygame.SRCALPHA)
    surface.fill((30, 10, 10))
    for x in range(3, 13):
        for y in range(4, 14):
            _draw_pixel(surface, x, y, (180, 50, 50))
    _draw_pixel(surface, 6, 8, (240, 200, 200))
    _draw_pixel(surface, 9, 8, (240, 200, 200))
    return surface


def _create_enemy2():
    surface = pygame.Surface((16, 16), pygame.SRCALPHA)
    surface.fill((10, 10, 30))
    for x in range(3, 13):
        for y in range(4, 14):
            _draw_pixel(surface, x, y, (60, 110, 200))
    for x in range(4, 12, 2):
        _draw_pixel(surface, x, 3, (180, 220, 255))
    return surface


def _create_bullet():
    surface = pygame.Surface((6, 6), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))
    for x in range(1, 5):
        for y in range(1, 5):
            _draw_pixel(surface, x, y, (120, 200, 255))
    return surface


def _create_floor():
    surface = pygame.Surface((16, 16), pygame.SRCALPHA)
    for y in range(16):
        for x in range(16):
            color = (40, 40, 50) if (x + y) % 2 == 0 else (50, 50, 60)
            _draw_pixel(surface, x, y, color)
    return surface


def _create_wall():
    surface = pygame.Surface((16, 16), pygame.SRCALPHA)
    surface.fill((70, 70, 90))
    for x in range(16):
        _draw_pixel(surface, x, 0, (120, 120, 140))
        _draw_pixel(surface, x, 15, (40, 40, 50))
    for y in range(16):
        _draw_pixel(surface, 0, y, (120, 120, 140))
        _draw_pixel(surface, 15, y, (40, 40, 50))
    _draw_pixel(surface, 4, 4, (150, 150, 170))
    _draw_pixel(surface, 11, 11, (150, 150, 170))
    return surface


def _create_door(opened):
    surface = pygame.Surface((16, 16), pygame.SRCALPHA)
    base = (40, 80, 50) if opened else (90, 30, 30)
    surface.fill(base)
    for x in range(3, 13):
        _draw_pixel(surface, x, 7, (160, 160, 160))
    return surface


def _create_prop_tape():
    surface = pygame.Surface((16, 16), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))
    for x in range(2, 14):
        _draw_pixel(surface, x, 8, (240, 230, 60))
    return surface


def _create_prop_mark():
    surface = pygame.Surface((16, 16), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))
    for i in range(4, 12):
        _draw_pixel(surface, i, i, (200, 50, 50))
        _draw_pixel(surface, i, 15 - i, (200, 50, 50))
    return surface


def _create_prop_curtain():
    surface = pygame.Surface((16, 16), pygame.SRCALPHA)
    for x in range(16):
        color = (120, 0, 80) if x % 2 == 0 else (160, 0, 120)
        for y in range(16):
            _draw_pixel(surface, x, y, color)
    return surface


def _create_item(color, accent):
    surface = pygame.Surface((16, 16), pygame.SRCALPHA)
    surface.fill((20, 20, 20))
    for x in range(3, 13):
        for y in range(3, 13):
            _draw_pixel(surface, x, y, color)
    _draw_pixel(surface, 7, 7, accent)
    _draw_pixel(surface, 8, 7, accent)
    _draw_pixel(surface, 7, 8, accent)
    _draw_pixel(surface, 8, 8, accent)
    return surface


def ensure_placeholders():
    _ensure_dir()
    creators = {
        "player.png": _create_player,
        "enemy1.png": _create_enemy1,
        "enemy2.png": _create_enemy2,
        "bullet.png": _create_bullet,
        "floor.png": _create_floor,
        "wall.png": _create_wall,
        "door_closed.png": lambda: _create_door(False),
        "door_open.png": lambda: _create_door(True),
        "prop_tape.png": _create_prop_tape,
        "prop_mark.png": _create_prop_mark,
        "prop_curtain.png": _create_prop_curtain,
        "item_mask.png": lambda: _create_item((200, 200, 200), (80, 80, 80)),
        "item_tape.png": lambda: _create_item((240, 230, 60), (160, 140, 40)),
        "item_script.png": lambda: _create_item((180, 160, 120), (90, 70, 40)),
        "item_spotlight.png": lambda: _create_item((255, 220, 120), (200, 140, 40)),
        "item_eraser.png": lambda: _create_item((220, 120, 160), (140, 60, 90)),
        "item_scissors.png": lambda: _create_item((160, 200, 220), (60, 90, 110)),
    }
    for filename, creator in creators.items():
        path = os.path.join(ASSET_DIR, filename)
        if not os.path.exists(path):
            try:
                surface = creator()
                _save_surface(surface, filename)
            except Exception as exc:
                _safe_print(f"[assets] 생성 실패 {filename}: {exc}")


def load_image(filename, size=None):
    path = os.path.join(ASSET_DIR, filename)
    try:
        image = pygame.image.load(path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except Exception as exc:
        _safe_print(f"[assets] 로드 실패 {filename}: {exc}")
        surface = pygame.Surface(size or (16, 16), pygame.SRCALPHA)
        surface.fill((100, 100, 100))
        return surface


def load_font(size):
    try:
        return pygame.font.SysFont("malgungothic", size)
    except Exception:
        try:
            return pygame.font.SysFont(None, size)
        except Exception:
            return pygame.font.Font(None, size)


def build_assets():
    ensure_placeholders()
    assets = {}
    assets["player"] = load_image(ASSET_FILES["player"])
    assets["enemy1"] = load_image(ASSET_FILES["enemy1"])
    assets["enemy2"] = load_image(ASSET_FILES["enemy2"])
    assets["bullet"] = load_image(ASSET_FILES["bullet"], size=(6, 6))
    assets["floor"] = load_image(ASSET_FILES["floor"])
    assets["wall"] = load_image(ASSET_FILES["wall"])
    assets["door_closed"] = load_image(ASSET_FILES["door_closed"])
    assets["door_open"] = load_image(ASSET_FILES["door_open"])
    assets["prop_tape"] = load_image(ASSET_FILES["prop_tape"])
    assets["prop_mark"] = load_image(ASSET_FILES["prop_mark"])
    assets["prop_curtain"] = load_image(ASSET_FILES["prop_curtain"])
    assets["item_mask"] = load_image(ASSET_FILES["item_mask"])
    assets["item_tape"] = load_image(ASSET_FILES["item_tape"])
    assets["item_script"] = load_image(ASSET_FILES["item_script"])
    assets["item_spotlight"] = load_image(ASSET_FILES["item_spotlight"])
    assets["item_eraser"] = load_image(ASSET_FILES["item_eraser"])
    assets["item_scissors"] = load_image(ASSET_FILES["item_scissors"])
    return assets
