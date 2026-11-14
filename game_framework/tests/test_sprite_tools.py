import os
import sys
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import pygame

from game_framework import sprite_tools


def make_surface(width=12, height=16):
    return pygame.Surface((width, height), pygame.SRCALPHA)


class TestSpriteTools(unittest.TestCase):
    def test_scale_surface_with_no_scale_returns_same_surface(self):
        surface = make_surface(10, 8)

        result = sprite_tools.scale_surface(surface)

        self.assertIs(result, surface)
        self.assertEqual(result.get_size(), (10, 8))

    def test_scale_surface_with_scale_doubles_size(self):
        surface = make_surface(10, 8)

        result = sprite_tools.scale_surface(surface, scale=2)

        self.assertEqual(result.get_size(), (20, 16))

    def test_scale_surface_with_width_preserves_aspect_ratio(self):
        surface = make_surface(10, 5)

        result = sprite_tools.scale_surface(surface, width=20)

        self.assertEqual(result.get_size(), (20, 10))

    def test_scale_surface_with_height_preserves_aspect_ratio(self):
        surface = make_surface(10, 5)

        result = sprite_tools.scale_surface(surface, height=20)

        self.assertEqual(result.get_size(), (40, 20))

    def test_load_sprite_sheet_row_returns_expected_number_of_frames(self):
        sheet = make_surface(16, 8)

        with patch.object(sprite_tools.pygame.image, "load", return_value=sheet):
            frames = sprite_tools.load_sprite_sheet_row("sprites.png", row=0, frame_width=4, frame_height=8, frame_count=4)

        self.assertEqual(len(frames), 4)

    def test_load_sprite_sheet_row_extracts_expected_frame_size(self):
        sheet = make_surface(16, 8)

        with patch.object(sprite_tools.pygame.image, "load", return_value=sheet):
            frames = sprite_tools.load_sprite_sheet_row("sprites.png", row=0, frame_width=4, frame_height=8, frame_count=4)

        self.assertEqual(frames[0].get_size(), (4, 8))

    def test_load_sprite_sheet_row_handles_scale(self):
        sheet = make_surface(16, 8)

        with patch.object(sprite_tools.pygame.image, "load", return_value=sheet):
            frames = sprite_tools.load_sprite_sheet_row("sprites.png", row=0, frame_width=4, frame_height=8, frame_count=4, scale=2)

        self.assertEqual(frames[0].get_size(), (8, 16))

    def test_load_sprite_sheet_row_rejects_invalid_frame_width(self):
        with self.assertRaisesRegex(ValueError, "frame_width"):
            sprite_tools.load_sprite_sheet_row("sprites.png", row=0, frame_width=0, frame_height=8, frame_count=4)

    def test_load_sprite_sheet_row_rejects_invalid_frame_height(self):
        with self.assertRaisesRegex(ValueError, "frame_height"):
            sprite_tools.load_sprite_sheet_row("sprites.png", row=0, frame_width=4, frame_height=0, frame_count=4)

    def test_load_sprite_sheet_row_rejects_invalid_frame_count(self):
        with self.assertRaisesRegex(ValueError, "frame_count"):
            sprite_tools.load_sprite_sheet_row("sprites.png", row=0, frame_width=4, frame_height=8, frame_count=0)

    def test_load_sprite_sheet_row_rejects_invalid_row(self):
        with self.assertRaisesRegex(ValueError, "row"):
            sprite_tools.load_sprite_sheet_row("sprites.png", row=-1, frame_width=4, frame_height=8, frame_count=4)

    def test_load_directional_sprite_sheet_returns_expected_direction_keys(self):
        sheet = make_surface(16, 16)

        with patch.object(sprite_tools.pygame.image, "load", return_value=sheet):
            frames = sprite_tools.load_directional_sprite_sheet("sprites.png", frame_width=4, frame_height=4, frame_count=4)

        self.assertEqual(set(frames.keys()), {"down", "left", "right", "up"})

    def test_load_directional_sprite_sheet_gives_each_direction_frames(self):
        sheet = make_surface(16, 16)

        with patch.object(sprite_tools.pygame.image, "load", return_value=sheet):
            frames = sprite_tools.load_directional_sprite_sheet("sprites.png", frame_width=4, frame_height=4, frame_count=4)

        self.assertEqual(len(frames["down"]), 4)
        self.assertEqual(len(frames["left"]), 4)
        self.assertEqual(len(frames["right"]), 4)
        self.assertEqual(len(frames["up"]), 4)

    def test_animation_starts_on_frame_zero(self):
        animation = sprite_tools.Animation(["walk_0", "walk_1"], frames_per_change=2)

        self.assertEqual(animation.current_frame_index, 0)
        self.assertEqual(animation.current_frame, "walk_0")

    def test_animation_advances_after_frames_per_change_updates(self):
        animation = sprite_tools.Animation(["walk_0", "walk_1"], frames_per_change=2)

        animation.update()
        self.assertEqual(animation.current_frame, "walk_0")
        animation.update()

        self.assertEqual(animation.current_frame, "walk_1")

    def test_animation_loops_back_after_enough_updates(self):
        animation = sprite_tools.Animation(["walk_0", "walk_1"], frames_per_change=2)

        for _ in range(4):
            animation.update()

        self.assertEqual(animation.current_frame_index, 0)
        self.assertEqual(animation.current_frame, "walk_0")

    def test_directional_animation_starts_with_valid_direction(self):
        frames = {"left": ["left_0"], "right": ["right_0"]}

        animation = sprite_tools.DirectionalAnimation(frames, starting_direction="right")

        self.assertEqual(animation.direction, "right")
        self.assertEqual(animation.current_frame, "right_0")

    def test_directional_animation_uses_first_direction_if_start_is_missing(self):
        frames = {"down": ["down_0"], "left": ["left_0"]}

        animation = sprite_tools.DirectionalAnimation(frames, starting_direction="right")

        self.assertEqual(animation.direction, "down")

    def test_directional_animation_changes_direction(self):
        frames = {"left": ["left_0"], "right": ["right_0"]}
        animation = sprite_tools.DirectionalAnimation(frames, starting_direction="right")

        animation.set_direction("left")

        self.assertEqual(animation.direction, "left")
        self.assertEqual(animation.current_frame, "left_0")

    def test_directional_animation_returns_frames_from_selected_direction(self):
        frames = {"left": ["left_0", "left_1"], "right": ["right_0", "right_1"]}
        animation = sprite_tools.DirectionalAnimation(frames, starting_direction="right", frames_per_change=1)

        animation.update()
        self.assertEqual(animation.current_frame, "right_1")
        animation.set_direction("left")

        self.assertEqual(animation.current_frame, "left_0")

    def test_directional_animation_loops_within_selected_direction(self):
        frames = {"left": ["left_0", "left_1"], "right": ["right_0", "right_1"]}
        animation = sprite_tools.DirectionalAnimation(frames, starting_direction="left", frames_per_change=1)

        animation.update()
        animation.update()

        self.assertEqual(animation.current_frame_index, 0)
        self.assertEqual(animation.current_frame, "left_0")


if __name__ == "__main__":
    unittest.main()
