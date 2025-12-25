import os
import random
import pygame

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")


def _make_pattern_surface(size, colors):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size
    for y in range(h):
        for x in range(w):
            surface.set_at((x, y), random.choice(colors))
    return surface


def _make_tile_surface(size, base_color, accent_color):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(base_color)
    for x in range(0, size[0], 2):
        surface.set_at((x, 0), accent_color)
        surface.set_at((x, size[1] - 1), accent_color)
    for y in range(0, size[1], 2):
        surface.set_at((0, y), accent_color)
        surface.set_at((size[0] - 1, y), accent_color)
    return surface


def load_image(name, size=(16, 16), placeholder_colors=None):
    path = os.path.join(ASSET_DIR, name)
    if os.path.exists(path):
        image = pygame.image.load(path).convert_alpha()
        return image
    if placeholder_colors is None:
        placeholder_colors = [(220, 220, 220), (180, 180, 180), (120, 120, 120)]
    return _make_pattern_surface(size, placeholder_colors)


def build_assets():
    assets = {
        "player": load_image("player.png", placeholder_colors=[(60, 200, 255), (30, 150, 220), (10, 90, 180)]),
        "chaser": load_image("enemy_chaser.png", placeholder_colors=[(255, 90, 90), (200, 40, 40), (120, 10, 10)]),
        "dasher": load_image("enemy_dasher.png", placeholder_colors=[(255, 180, 50), (220, 140, 20), (150, 90, 10)]),
        "bullet": load_image("bullet.png", size=(6, 6), placeholder_colors=[(120, 200, 255), (80, 160, 220)]),
        "floor": load_image("floor.png", placeholder_colors=[(40, 40, 50), (30, 30, 40), (50, 50, 60)]),
        "wall": load_image("wall.png", placeholder_colors=[(90, 90, 110), (70, 70, 90), (120, 120, 140)]),
        "door_closed": load_image("door_closed.png", placeholder_colors=[(80, 30, 30), (120, 50, 50), (140, 70, 70)]),
        "door_open": load_image("door_open.png", placeholder_colors=[(30, 80, 30), (50, 120, 50), (70, 140, 70)]),
        "prop_tape": load_image("prop_tape.png", placeholder_colors=[(240, 230, 60), (200, 190, 40)]),
        "prop_mark": load_image("prop_mark.png", placeholder_colors=[(200, 50, 50), (120, 20, 20)]),
        "prop_curtain": load_image("prop_curtain.png", placeholder_colors=[(120, 0, 80), (160, 0, 120)]),
    }

    item_names = [
        "paper_mask",
        "tape",
        "script",
        "spotlight",
        "eraser",
        "scissors",
    ]
    for name in item_names:
        assets[f"item_{name}"] = load_image(f"item_{name}.png", placeholder_colors=[(200, 200, 200), (150, 150, 150)])

    assets["ui_heart"] = _make_tile_surface((8, 8), (200, 40, 60), (255, 120, 140))
    return assets
