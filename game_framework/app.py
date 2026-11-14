from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, cast

try:
    import pygame
except ModuleNotFoundError:
    from .pygame_stub import pygame

from .game_object import Color, GameObject, ScreenSize

EventHandler = Callable[["GameApp", "pygame.event.Event"], None]


class SoundEffect(Protocol):
    def set_volume(self, volume: float) -> None:
        """Set this sound's volume."""
        ...

    def play(self) -> object:
        """Play this sound once."""
        ...


def _check_volume(volume: float) -> None:
    if volume < 0.0 or volume > 1.0:
        raise ValueError("Volume must be between 0.0 and 1.0.")


class GameApp:
    """The main game controller used by student projects."""

    def __init__(
        self,
        width: int = 800,
        height: int = 450,
        title: str = "Game App",
        bg_color: Color = (240, 246, 255),
        fps: int = 30,
    ) -> None:
        """Create a game window with a size, title, background colour, and speed."""
        self._running = True
        self._display_surface: pygame.Surface | None = None
        #TODO: 2026-06-02 Consider changing ScreenSize and not use it as this information is available from app
        self._display_surface_size: ScreenSize = (width, height)
        self.title = title
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.bg_color = bg_color
        self.game_objects: dict[str, GameObject] = {}
        self.players: dict[str, GameObject] = {}
        self.sounds: dict[str, SoundEffect] = {}
        self.keydown_handler: EventHandler | None = None
        self.keyup_handler: EventHandler | None = None
        self.quit_handler: EventHandler | None = None
        self.any_event_handler: EventHandler | None = None


    def _ensure_mixer(self) -> None:
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()

    def set_keydown_handler(self, handler: EventHandler) -> None:
        """Attach a function that runs when a key is pressed."""
        self.keydown_handler = handler

    def set_keyup_handler(self, handler: EventHandler) -> None:
        """Attach a function that runs when a key is released."""
        self.keyup_handler = handler

    def set_quit_handler(self, handler: EventHandler) -> None:
        """Attach a function that runs when the game window closes."""
        self.quit_handler = handler

    def set_any_event_handler(self, handler: EventHandler) -> None:
        """Attach a function that runs for every Pygame event."""
        self.any_event_handler = handler

    def add_object(self, name: str, game_object: GameObject) -> None:
        """Add a named object so it can be updated, drawn, and found later."""
        game_object.app = self
        self.game_objects[name] = game_object

    def remove_object(self, name: str) -> None:
        """Remove a named object from the game."""
        del self.game_objects[name]

    def get_object(self, name: str) -> GameObject | None:
        """Return a named GameObject, or None if it is not in the game."""
        return self.game_objects.get(name)

    def add_player(self, name: str, player: GameObject) -> None:
        """Add a named player and also store it as a normal game object."""
        player.app = self
        self.players[name] = player
        self.add_object(name, player)

    def get_player(self, name: str) -> GameObject | None:
        """Return a named player, or None if it has not been added."""
        return self.players.get(name)

    def add_sound(self, name: str, path: str, volume: float = 1.0) -> None:
        """Load a sound file and store it with a name."""
        _check_volume(volume)
        self._ensure_mixer()
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        self.sounds[name] = sound

    def set_sound_volume(self, name: str, volume: float) -> None:
        """Set the volume for a sound that was added with add_sound."""
        _check_volume(volume)
        sound = self.sounds.get(name)
        if sound is None:
            raise KeyError(f"No sound named {name!r} has been added.")
        sound.set_volume(volume)

    def play_sound(self, name: str) -> None:
        """Play a sound that was added with add_sound."""
        sound = self.sounds.get(name)
        if sound is None:
            raise KeyError(f"No sound named {name!r} has been added.")
        sound.play()

    def set_background_music(self, path: str, volume: float = 1.0) -> None:
        """Load background music and set its volume."""
        _check_volume(volume)
        self._ensure_mixer()
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)

    def set_background_music_volume(self, volume: float) -> None:
        """Set the volume for the background music."""
        _check_volume(volume)
        pygame.mixer.music.set_volume(volume)

    def play_background_music(self, loops: int = -1) -> None:
        """Play the background music, looping forever by default."""
        pygame.mixer.music.play(loops)

    def stop_background_music(self) -> None:
        """Stop the background music."""
        pygame.mixer.music.stop()

    def get_size(self) -> ScreenSize:
        """Return the game window size as (width, height)."""
        return self._display_surface_size

    def on_init(self) -> bool:
        """Start pygame and create the display window."""
        pygame.init()
        self._display_surface = pygame.display.set_mode(self._display_surface_size)
        pygame.display.set_caption(self.title)
        return True

    def on_event(self, event: "pygame.event.Event") -> None:
        """Handle one pygame event, such as a key press or quit event."""
        if self.any_event_handler is not None:
            self.any_event_handler(self, event)

        if event.type == pygame.QUIT:
            if self.quit_handler is not None:
                self.quit_handler(self, event)
            else:
                self._running = False
        elif event.type == pygame.KEYDOWN:
            if self.keydown_handler is not None:
                self.keydown_handler(self, event)
        elif event.type == pygame.KEYUP:
            if self.keyup_handler is not None:
                self.keyup_handler(self, event)

    def on_loop(self) -> None:
        """Update every object in the game once."""
        # Copy current objects so update handlers can safely add or remove objects.
        for game_object in list(self.game_objects.values()):
            game_object.update(self.get_size())

    def on_render(self) -> None:
        """Clear the screen, draw every object, and show the new frame."""
        surface = cast("pygame.Surface", self._display_surface)
        surface.fill(self.bg_color)
        background = self.game_objects.get("background")
        if background is not None:
            background.draw(surface)

        for name, game_object in self.game_objects.items():
            if name == "background":
                continue
            game_object.draw(surface)
        pygame.display.flip()

    def on_cleanup(self) -> None:
        """Close pygame when the game finishes."""
        pygame.quit()

    def on_execute(self) -> None:
        """Run the full game loop until the game is closed."""
        if self.on_init() is False:
            self._running = False
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            self.clock.tick(self.fps)
        self.on_cleanup()

    def get_collision_edge(self, moving_object: GameObject, other_object: GameObject) -> str:
        """
        Work out which edge of other_object was hit by moving_object.

        This version works even if both objects are moving.
        It compares their relative movement, which means how moving_object
        moved compared with other_object.
        """

        # Work out how moving_object moved compared with other_object.
        relative_vx = moving_object.vx - other_object.vx
        relative_vy = moving_object.vy - other_object.vy

        # Estimate where moving_object was compared with other_object
        # in the previous frame.
        previous_x = moving_object.x - relative_vx
        previous_y = moving_object.y - relative_vy

        previous_left = previous_x
        previous_right = previous_x + moving_object.width
        previous_top = previous_y
        previous_bottom = previous_y + moving_object.height

        other_left = other_object.x
        other_right = other_object.x + other_object.width
        other_top = other_object.y
        other_bottom = other_object.y + other_object.height

        if relative_vx > 0 and previous_right <= other_left:
            return "left"

        if relative_vx < 0 and previous_left >= other_right:
            return "right"

        if relative_vy > 0 and previous_bottom <= other_top:
            return "top"

        if relative_vy < 0 and previous_top >= other_bottom:
            return "bottom"

        horizontal_overlap = min(
            abs(moving_object.x + moving_object.width - other_left),
            abs(other_right - moving_object.x)
        )

        vertical_overlap = min(
            abs(moving_object.y + moving_object.height - other_top),
            abs(other_bottom - moving_object.y)
        )

        if horizontal_overlap <= vertical_overlap:
            if moving_object.x < other_object.x:
                return "left"
            else:
                return "right"

        if moving_object.y < other_object.y:
            return "top"
        else:
            return "bottom"

    def is_colliding(self, first: GameObject, second: GameObject) -> bool:
        """
        Check whether two rectangular game objects are touching.

        Each GameObject has:
            x: the x-coordinate of its left edge\n
            y: the y-coordinate of its top edge\n
            width: how wide the object is\n
            height: how tall the object is

        This function uses rectangle collision detection.

        It returns:
            True if the two objects overlap.
            False if the two objects are separate.

        Two objects are colliding if:
            - the left edge of the first object is before the right edge of the second object\n
            - the right edge of the first object is after the left edge of the second object\n
            - the top edge of the first object is above the bottom edge of the second object\n
            - the bottom edge of the first object is below the top edge of the second object\n
        """

        return (
            # The first object's left edge is left of the second object's right edge.
                first.x < second.x + second.width

                # The first object's right edge is right of the second object's left edge.
                and first.x + first.width > second.x

                # The first object's top edge is above the second object's bottom edge.
                and first.y < second.y + second.height

                # The first object's bottom edge is below the second object's top edge.
                and first.y + first.height > second.y
        )

App = GameApp
