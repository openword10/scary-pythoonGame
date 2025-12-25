import os
import pygame

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

FILE_NAMES = {
    "player": "player.png",
    "enemy1": "enemy1.png",
    "enemy2": "enemy2.png",
    "tile_floor": "tile_floor.png",
    "tile_wall": "tile_wall.png",
    "coin": "coin.png",
    "goal": "goal.png",
    "bg": "bg.png",
}


def _safe_print(message):
    try:
        print(message)
    except Exception:
        pass


def ensure_asset_dir():
    try:
        os.makedirs(ASSET_DIR, exist_ok=True)
    except Exception as exc:
        _safe_print(f"[assets] 폴더 생성 실패: {exc}")


def _draw_pixel(surface, x, y, color):
    if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
        surface.set_at((x, y), color)


def _draw_label(surface, text, font):
    try:
        label = font.render(text, True, (10, 10, 10))
        rect = label.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
        surface.blit(label, rect)
    except Exception:
        pass


def _placeholder_player(font):
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    surf.fill((70, 70, 90))
    for x in range(4, 12):
        for y in range(3, 13):
            _draw_pixel(surf, x, y, (200, 200, 210))
    _draw_pixel(surf, 6, 7, (30, 30, 40))
    _draw_pixel(surf, 9, 7, (30, 30, 40))
    _draw_pixel(surf, 7, 10, (120, 80, 80))
    _draw_pixel(surf, 8, 10, (120, 80, 80))
    _draw_label(surf, "주인공", font)
    return surf


def _placeholder_enemy1(font):
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    surf.fill((40, 10, 10))
    for x in range(3, 13):
        for y in range(4, 14):
            _draw_pixel(surf, x, y, (170, 50, 50))
    _draw_pixel(surf, 6, 8, (230, 200, 200))
    _draw_pixel(surf, 9, 8, (230, 200, 200))
    _draw_label(surf, "괴물1", font)
    return surf


def _placeholder_enemy2(font):
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    surf.fill((10, 10, 40))
    for x in range(3, 13):
        for y in range(4, 14):
            _draw_pixel(surf, x, y, (60, 110, 200))
    for x in range(4, 12, 2):
        _draw_pixel(surf, x, 3, (180, 220, 255))
    _draw_label(surf, "괴물2", font)
    return surf


def _placeholder_tile_floor():
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    for y in range(16):
        for x in range(16):
            color = (40, 40, 50) if (x + y) % 2 == 0 else (50, 50, 60)
            _draw_pixel(surf, x, y, color)
    return surf


def _placeholder_tile_wall():
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    surf.fill((70, 70, 90))
    for x in range(16):
        _draw_pixel(surf, x, 0, (120, 120, 140))
        _draw_pixel(surf, x, 15, (40, 40, 50))
    for y in range(16):
        _draw_pixel(surf, 0, y, (120, 120, 140))
        _draw_pixel(surf, 15, y, (40, 40, 50))
    return surf


def _placeholder_coin(font):
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.circle(surf, (240, 200, 60), (8, 8), 6)
    _draw_label(surf, "조각", font)
    return surf


def _placeholder_goal(font):
    surf = pygame.Surface((16, 24), pygame.SRCALPHA)
    surf.fill((20, 20, 30))
    pygame.draw.rect(surf, (120, 180, 120), pygame.Rect(5, 4, 6, 16))
    _draw_label(surf, "막", font)
    return surf


def _placeholder_bg():
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    surf.fill((15, 15, 25))
    for x in range(0, 16, 4):
        pygame.draw.line(surf, (25, 15, 30), (x, 0), (x, 15))
    return surf


def load_font(size):
    try:
        return pygame.font.SysFont("malgungothic", size)
    except Exception:
        try:
            return pygame.font.SysFont(None, size)
        except Exception:
            return pygame.font.Font(None, size)


def save_placeholder(filename, surface):
    path = os.path.join(ASSET_DIR, filename)
    try:
        pygame.image.save(surface, path)
    except Exception as exc:
        _safe_print(f"[assets] 저장 실패 {filename}: {exc}")


def ensure_placeholders():
    ensure_asset_dir()
    font = load_font(8)
    creators = {
        FILE_NAMES["player"]: lambda: _placeholder_player(font),
        FILE_NAMES["enemy1"]: lambda: _placeholder_enemy1(font),
        FILE_NAMES["enemy2"]: lambda: _placeholder_enemy2(font),
        FILE_NAMES["tile_floor"]: _placeholder_tile_floor,
        FILE_NAMES["tile_wall"]: _placeholder_tile_wall,
        FILE_NAMES["coin"]: lambda: _placeholder_coin(font),
        FILE_NAMES["goal"]: lambda: _placeholder_goal(font),
        FILE_NAMES["bg"]: _placeholder_bg,
    }
    for filename, creator in creators.items():
        path = os.path.join(ASSET_DIR, filename)
        if not os.path.exists(path):
            try:
                surface = creator()
                save_placeholder(filename, surface)
            except Exception as exc:
                _safe_print(f"[assets] placeholder 생성 실패 {filename}: {exc}")


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
        surface.fill((120, 120, 120))
        return surface


def build_assets():
    ensure_placeholders()
    assets = {
        "player": load_image(FILE_NAMES["player"]),
        "enemy1": load_image(FILE_NAMES["enemy1"]),
        "enemy2": load_image(FILE_NAMES["enemy2"]),
        "tile_floor": load_image(FILE_NAMES["tile_floor"]),
        "tile_wall": load_image(FILE_NAMES["tile_wall"]),
        "coin": load_image(FILE_NAMES["coin"]),
        "goal": load_image(FILE_NAMES["goal"]),
        "bg": load_image(FILE_NAMES["bg"]),
    }
    return assets
