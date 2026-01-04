import random
import pygame


class Item:
    def __init__(self, name, description, icon_key, apply_fn):
        self.name = name
        self.description = description
        self.icon_key = icon_key
        self.apply_fn = apply_fn

    def apply(self, player, game, room):
        # 아이템 효과 적용
        self.apply_fn(player, game, room)


class ItemPickup:
    def __init__(self, x, y, item):
        self.rect = pygame.Rect(x, y, 12, 12)
        self.item = item
        self.collected = False


class ItemLibrary:
    def __init__(self):
        self.items = []
        self._build_items()

    def _build_items(self):
        # 아이템 목록 구성 (효과는 람다로 전달)
        self.items = [
            Item(
                "종이 가면",
                "피해 감소 +1",
                "item_mask",
                lambda player, game, room: setattr(player, "damage_reduction", player.damage_reduction + 1),
            ),
            Item(
                "테이프",
                "임시 보호막 1회",
                "item_tape",
                lambda player, game, room: setattr(player, "shield", player.shield + 1),
            ),
            Item(
                "대본",
                "다음 방 힌트",
                "item_script",
                lambda player, game, room: game.reveal_next_room_hint(),
            ),
            Item(
                "스포트라이트",
                "탄 속도↑ 적도 빠르게",
                "item_spotlight",
                lambda player, game, room: (game.boost_projectiles(), game.boost_enemies()),
            ),
            Item(
                "지우개",
                "방 리셋 1회",
                "item_eraser",
                lambda player, game, room: setattr(player, "room_reset_charges", player.room_reset_charges + 1),
            ),
            Item(
                "가위",
                "이동 속도 증가",
                "item_scissors",
                lambda player, game, room: setattr(player, "speed", player.speed + 15),
            ),
        ]

    def random_item(self):
        return random.choice(self.items)
