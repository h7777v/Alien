import os
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import pygame

from game_framework.sprite_object import SpriteObject
from game_framework.sprite_tools import Animation, DirectionalAnimation


def make_surface(width: int = 24, height: int = 24) -> pygame.Surface:
    return pygame.Surface((width, height), pygame.SRCALPHA)


def record_draw_handler(obj: SpriteObject, surface: pygame.Surface) -> None:
    obj.draw_calls.append((obj, surface))


class TestSpriteObject(unittest.TestCase):
    def test_draw_uses_animation_frame_when_no_handler_is_attached(self):
        target = make_surface()
        frame = make_surface(6, 6)
        frame.fill((255, 0, 0, 255))
        sprite = SpriteObject(x=4, y=5, width=6, height=6)
        sprite.animation = Animation([frame])

        sprite.draw(target)

        self.assertEqual(target.get_at((4, 5)), pygame.Color(255, 0, 0, 255))

    def test_draw_prefers_directional_animation_frame(self):
        target = make_surface()
        animation_frame = make_surface(6, 6)
        animation_frame.fill((255, 0, 0, 255))
        directional_frame = make_surface(6, 6)
        directional_frame.fill((0, 255, 0, 255))
        sprite = SpriteObject(x=3, y=4, width=6, height=6)
        sprite.animation = Animation([animation_frame])
        sprite.directional_animation = DirectionalAnimation({"right": [directional_frame]})

        sprite.draw(target)

        self.assertEqual(target.get_at((3, 4)), pygame.Color(0, 255, 0, 255))

    def test_set_animation_changes_directional_animation_direction(self):
        sprite = SpriteObject()
        sprite.directional_animation = DirectionalAnimation({"left": ["left_0"], "right": ["right_0"]})

        sprite.set_animation("right")

        self.assertEqual(sprite.directional_animation.direction, "right")

    def test_set_animation_changes_animation_when_it_is_directional(self):
        sprite = SpriteObject()
        sprite.animation = DirectionalAnimation({"left": ["left_0"], "right": ["right_0"]})

        sprite.set_animation("left")

        self.assertEqual(sprite.animation.direction, "left")

    def test_set_animation_requires_directional_animation(self):
        sprite = SpriteObject()
        sprite.animation = Animation(["frame_0"])

        with self.assertRaisesRegex(ValueError, "directional animation"):
            sprite.set_animation("right")

    def test_update_animation_advances_directional_animation(self):
        sprite = SpriteObject()
        sprite.directional_animation = DirectionalAnimation(
            {"right": ["right_0", "right_1"]},
            frames_per_change=1,
        )

        sprite.update_animation()

        self.assertEqual(sprite.directional_animation.current_frame, "right_1")

    def test_update_animation_advances_simple_animation(self):
        sprite = SpriteObject()
        sprite.animation = Animation(["frame_0", "frame_1"], frames_per_change=1)

        sprite.update_animation()

        self.assertEqual(sprite.animation.current_frame, "frame_1")

    def test_draw_uses_colour_animation_frame(self):
        target = make_surface()
        sprite = SpriteObject(x=5, y=6, width=6, height=6)
        sprite.animation = Animation([(255, 220, 40)])

        sprite.draw(target)

        self.assertEqual(target.get_at((5, 6)), pygame.Color(255, 220, 40, 255))

    def test_draw_uses_static_image_when_no_animation_exists(self):
        target = make_surface()
        image = make_surface(6, 6)
        image.fill((0, 0, 255, 255))
        sprite = SpriteObject(x=2, y=3, width=6, height=6)
        sprite.image = image

        sprite.draw(target)

        self.assertEqual(target.get_at((2, 3)), pygame.Color(0, 0, 255, 255))

    def test_draw_skips_inactive_sprite_without_handler(self):
        target = make_surface()
        frame = make_surface(6, 6)
        frame.fill((255, 0, 0, 255))
        sprite = SpriteObject(x=4, y=5, width=6, height=6)
        sprite.animation = Animation([frame])
        sprite.active = False

        sprite.draw(target)

        self.assertEqual(target.get_at((4, 5)), pygame.Color(0, 0, 0, 0))

    def test_draw_handler_still_overrides_default_drawing(self):
        target = make_surface()
        frame = make_surface(6, 6)
        frame.fill((255, 0, 0, 255))
        sprite = SpriteObject(x=4, y=5, width=6, height=6)
        sprite.animation = Animation([frame])
        sprite.draw_calls = []
        sprite.set_draw_handler(record_draw_handler)

        sprite.draw(target)

        self.assertEqual(sprite.draw_calls, [(sprite, target)])
        self.assertEqual(target.get_at((4, 5)), pygame.Color(0, 0, 0, 0))


if __name__ == "__main__":
    unittest.main()
