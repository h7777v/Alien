import unittest
from unittest.mock import patch

from game_framework.app import GameApp


class FakeSurface:
    def __init__(self) -> None:
        self.fills = []

    def fill(self, color) -> None:
        self.fills.append(color)


class RecordingObject:
    def __init__(self, name: str, calls: list[str]) -> None:
        self.name = name
        self.calls = calls

    def draw(self, surface) -> None:
        self.calls.append(self.name)


class FakeSound:
    def __init__(self) -> None:
        self.play_count = 0
        self.volume = 1.0

    def set_volume(self, volume: float) -> None:
        self.volume = volume

    def play(self) -> None:
        self.play_count += 1


class TestGameAppRender(unittest.TestCase):
    def test_on_render_draws_background_first(self):
        calls: list[str] = []
        app = GameApp()
        app._display_surface = FakeSurface()
        app.add_object("player", RecordingObject("player", calls))
        app.add_object("background", RecordingObject("background", calls))
        app.add_object("coin", RecordingObject("coin", calls))

        with patch("game_framework.app.pygame.display.flip"):
            app.on_render()

        self.assertEqual(calls, ["background", "player", "coin"])


class TestGameAppSound(unittest.TestCase):
    def test_add_sound_loads_named_sound(self):
        app = GameApp()
        sound = FakeSound()

        with (
            patch("game_framework.app.pygame.mixer.get_init", return_value=(44100, -16, 2)),
            patch("game_framework.app.pygame.mixer.init") as init_mixer,
            patch("game_framework.app.pygame.mixer.Sound", return_value=sound) as load_sound,
        ):
            app.add_sound("collect", "sounds/collect.wav")

        init_mixer.assert_not_called()
        load_sound.assert_called_once_with("sounds/collect.wav")
        self.assertIs(app.sounds["collect"], sound)
        self.assertEqual(sound.volume, 1.0)

    def test_add_sound_initializes_mixer_when_needed(self):
        app = GameApp()
        sound = FakeSound()

        with (
            patch("game_framework.app.pygame.mixer.get_init", return_value=None),
            patch("game_framework.app.pygame.mixer.init") as init_mixer,
            patch("game_framework.app.pygame.mixer.Sound", return_value=sound),
        ):
            app.add_sound("hit", "sounds/hit.wav")

        init_mixer.assert_called_once_with()
        self.assertIs(app.sounds["hit"], sound)

    def test_add_sound_sets_sound_volume(self):
        app = GameApp()
        sound = FakeSound()

        with (
            patch("game_framework.app.pygame.mixer.get_init", return_value=(44100, -16, 2)),
            patch("game_framework.app.pygame.mixer.Sound", return_value=sound),
        ):
            app.add_sound("laser", "sounds/laser.wav", volume=0.4)

        self.assertEqual(sound.volume, 0.4)

    def test_set_sound_volume_updates_named_sound(self):
        app = GameApp()
        sound = FakeSound()
        app.sounds["collect"] = sound

        app.set_sound_volume("collect", 0.25)

        self.assertEqual(sound.volume, 0.25)

    def test_set_sound_volume_rejects_missing_sound_name(self):
        app = GameApp()

        with self.assertRaisesRegex(KeyError, "missing"):
            app.set_sound_volume("missing", 0.5)

    def test_sound_volume_must_be_between_zero_and_one(self):
        app = GameApp()

        with self.assertRaisesRegex(ValueError, "between 0.0 and 1.0"):
            app.add_sound("collect", "sounds/collect.wav", volume=1.5)

    def test_play_sound_plays_named_sound(self):
        app = GameApp()
        sound = FakeSound()
        app.sounds["collect"] = sound

        app.play_sound("collect")

        self.assertEqual(sound.play_count, 1)

    def test_play_sound_rejects_missing_sound_name(self):
        app = GameApp()

        with self.assertRaisesRegex(KeyError, "missing"):
            app.play_sound("missing")

    def test_set_background_music_loads_music_and_sets_volume(self):
        app = GameApp()

        with (
            patch("game_framework.app.pygame.mixer.get_init", return_value=(44100, -16, 2)),
            patch("game_framework.app.pygame.mixer.music.load") as load_music,
            patch("game_framework.app.pygame.mixer.music.set_volume") as set_volume,
        ):
            app.set_background_music("sounds/background.mp3", volume=0.3)

        load_music.assert_called_once_with("sounds/background.mp3")
        set_volume.assert_called_once_with(0.3)

    def test_set_background_music_initializes_mixer_when_needed(self):
        app = GameApp()

        with (
            patch("game_framework.app.pygame.mixer.get_init", return_value=None),
            patch("game_framework.app.pygame.mixer.init") as init_mixer,
            patch("game_framework.app.pygame.mixer.music.load"),
            patch("game_framework.app.pygame.mixer.music.set_volume"),
        ):
            app.set_background_music("sounds/background.mp3")

        init_mixer.assert_called_once_with()

    def test_set_background_music_volume_updates_music_volume(self):
        app = GameApp()

        with patch("game_framework.app.pygame.mixer.music.set_volume") as set_volume:
            app.set_background_music_volume(0.6)

        set_volume.assert_called_once_with(0.6)

    def test_background_music_volume_must_be_between_zero_and_one(self):
        app = GameApp()

        with self.assertRaisesRegex(ValueError, "between 0.0 and 1.0"):
            app.set_background_music("sounds/background.mp3", volume=-0.1)

    def test_play_background_music_loops_forever_by_default(self):
        app = GameApp()

        with patch("game_framework.app.pygame.mixer.music.play") as play_music:
            app.play_background_music()

        play_music.assert_called_once_with(-1)

    def test_stop_background_music_stops_music(self):
        app = GameApp()

        with patch("game_framework.app.pygame.mixer.music.stop") as stop_music:
            app.stop_background_music()

        stop_music.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
