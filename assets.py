import os
import pygame

from setting import (
    PLAYER_RUN_FRAMES,
    PLAYER_RUN_FRAME_SIZE,
    PLAYER_IDLE_FRAMES,
    PLAYER_IDLE_FRAME_SIZE,
    PLAYER_RUN_FILE,
    PLAYER_IDLE_FILE,
    ENEMY1_FRAMES,
    ENEMY1_FRAME_SIZE,
    ENEMY1_FILE,
    ENEMY2_FRAMES,
    ENEMY2_FRAME_SIZE,
    ENEMY2_FILE,
)

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

FILE_NAMES = {
    "player": "player.png",
    "enemy1": "enemy1.png",
    "enemy2": "enemy2.png",
    "tile_floor": "tile_floor.png",
    "tile_wall": "tile_wall.png",
    "heart": "heart.png",
    "goal": "goal.png",
    "bg": "bg.png",
    "blood": "blood.png",
    "attack": "attack.png",
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


def _placeholder_player_sheet(font):
    sheet = pygame.Surface((PLAYER_RUN_FRAME_SIZE[0] * PLAYER_RUN_FRAMES, PLAYER_RUN_FRAME_SIZE[1]), pygame.SRCALPHA)
    for frame in range(PLAYER_RUN_FRAMES):
        x0 = frame * PLAYER_RUN_FRAME_SIZE[0]
        frame_surf = pygame.Surface(PLAYER_RUN_FRAME_SIZE, pygame.SRCALPHA)
        frame_surf.fill((40, 40, 55))
        for x in range(10, 22):
            for y in range(8, 24):
                _draw_pixel(frame_surf, x, y, (200, 200, 215))
        _draw_pixel(frame_surf, 13, 13, (30, 30, 40))
        _draw_pixel(frame_surf, 18, 13, (30, 30, 40))
        _draw_pixel(frame_surf, 14, 18, (140, 80, 80))
        _draw_pixel(frame_surf, 17, 18, (140, 80, 80))
        _draw_label(frame_surf, "주인공", font)
        sheet.blit(frame_surf, (x0, 0))
    return sheet


def _placeholder_enemy1(font):
    sheet = pygame.Surface((ENEMY1_FRAME_SIZE[0] * ENEMY1_FRAMES, ENEMY1_FRAME_SIZE[1]), pygame.SRCALPHA)
    for frame in range(ENEMY1_FRAMES):
        surf = pygame.Surface(ENEMY1_FRAME_SIZE, pygame.SRCALPHA)
        surf.fill((40, 10, 10))
        for x in range(3, 13):
            for y in range(4, 14):
                _draw_pixel(surf, x, y, (170, 50, 50))
        if frame % 2 == 0:
            _draw_pixel(surf, 6, 8, (230, 200, 200))
            _draw_pixel(surf, 9, 8, (230, 200, 200))
        else:
            _draw_pixel(surf, 5, 8, (230, 200, 200))
            _draw_pixel(surf, 10, 8, (230, 200, 200))
        _draw_label(surf, "괴물1", font)
        sheet.blit(surf, (frame * ENEMY1_FRAME_SIZE[0], 0))
    return sheet


def _placeholder_enemy2(font):
    sheet = pygame.Surface((ENEMY2_FRAME_SIZE[0] * ENEMY2_FRAMES, ENEMY2_FRAME_SIZE[1]), pygame.SRCALPHA)
    for frame in range(ENEMY2_FRAMES):
        surf = pygame.Surface(ENEMY2_FRAME_SIZE, pygame.SRCALPHA)
        surf.fill((10, 10, 40))
        for x in range(3, 13):
            for y in range(4, 14):
                _draw_pixel(surf, x, y, (60, 110, 200))
        for x in range(4, 12, 2):
            _draw_pixel(surf, x, 3 + (frame % 2), (180, 220, 255))
        _draw_label(surf, "괴물2", font)
        sheet.blit(surf, (frame * ENEMY2_FRAME_SIZE[0], 0))
    return sheet


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


def _placeholder_heart(font):
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.circle(surf, (220, 60, 80), (6, 6), 4)
    pygame.draw.circle(surf, (220, 60, 80), (10, 6), 4)
    pygame.draw.polygon(surf, (220, 60, 80), [(2, 7), (14, 7), (8, 14)])
    _draw_label(surf, "하트", font)
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


def _placeholder_blood():
    surf = pygame.Surface((4, 4), pygame.SRCALPHA)
    surf.fill((180, 40, 40))
    return surf


def _placeholder_attack():
    surf = pygame.Surface((16, 12), pygame.SRCALPHA)
    pygame.draw.rect(surf, (240, 220, 180), pygame.Rect(1, 1, 14, 10), 1)
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
        FILE_NAMES["player"]: lambda: _placeholder_player_sheet(font),
        FILE_NAMES["enemy1"]: lambda: _placeholder_enemy1(font),
        FILE_NAMES["enemy2"]: lambda: _placeholder_enemy2(font),
        FILE_NAMES["tile_floor"]: _placeholder_tile_floor,
        FILE_NAMES["tile_wall"]: _placeholder_tile_wall,
        FILE_NAMES["heart"]: lambda: _placeholder_heart(font),
        FILE_NAMES["goal"]: lambda: _placeholder_goal(font),
        FILE_NAMES["bg"]: _placeholder_bg,
        FILE_NAMES["blood"]: _placeholder_blood,
        FILE_NAMES["attack"]: _placeholder_attack,
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


def load_sprite_frames(filename, frame_size, frames_count):
    image = load_image(filename)
    width, height = image.get_size()
    if width >= frame_size[0] * frames_count and height >= frame_size[1]:
        frames = []
        for idx in range(frames_count):
            frame = pygame.Surface(frame_size, pygame.SRCALPHA)
            frame.blit(image, (0, 0), pygame.Rect(idx * frame_size[0], 0, frame_size[0], frame_size[1]))
            frames.append(frame)
        return frames
    return [pygame.transform.scale(image, frame_size)]


def load_player_run_frames():
    return load_sprite_frames(PLAYER_RUN_FILE, PLAYER_RUN_FRAME_SIZE, PLAYER_RUN_FRAMES)


def load_player_idle_frames():
    return load_sprite_frames(PLAYER_IDLE_FILE, PLAYER_IDLE_FRAME_SIZE, PLAYER_IDLE_FRAMES)


def load_enemy1_frames():
    return load_sprite_frames(ENEMY1_FILE, ENEMY1_FRAME_SIZE, ENEMY1_FRAMES)


def load_enemy2_frames():
    return load_sprite_frames(ENEMY2_FILE, ENEMY2_FRAME_SIZE, ENEMY2_FRAMES)


def build_assets():
    ensure_placeholders()
    assets = {
        "player_run_frames": load_player_run_frames(),
        "player_idle_frames": load_player_idle_frames(),
        "enemy1_frames": load_enemy1_frames(),
        "enemy2_frames": load_enemy2_frames(),
        "tile_floor": load_image(FILE_NAMES["tile_floor"]),
        "tile_wall": load_image(FILE_NAMES["tile_wall"]),
        "heart": load_image(FILE_NAMES["heart"]),
        "goal": load_image(FILE_NAMES["goal"]),
        "bg": load_image(FILE_NAMES["bg"]),
        "blood": load_image(FILE_NAMES["blood"], size=(4, 4)),
        "attack": load_image(FILE_NAMES["attack"], size=(16, 12)),
    }
    return assets
