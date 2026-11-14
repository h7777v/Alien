from __future__ import annotations

from collections.abc import Callable


try:
    import pygame
except ModuleNotFoundError:
    from .pygame_stub import pygame

Color = tuple[int, int, int]
ScreenSize = tuple[int, int]
UpdateHandler = Callable[["GameObject", ScreenSize], None]
DrawHandler = Callable[["GameObject", "pygame.Surface"], None]


class GameObject:
    """A basic object that can be placed, updated, and drawn in a game."""

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 50,
        height: int = 50,
        color: Color = (0, 0, 0),
    ) -> None:
        """Create an object with a position, size, colour, and optional handlers."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.vx = 0
        self.vy = 0
        self._active = True
        self.update_handler: UpdateHandler | None = None
        self.draw_handler: DrawHandler | None = None
        self.app = None

    @property
    def active(self) -> bool:
        """Return whether this object is currently active."""
        return self._active

    @active.setter
    def active(self, value: bool) -> None:
        self._active = value

    @property
    def is_active(self) -> bool:
        """Return whether this object is currently active."""
        return self._active

    @is_active.setter
    def is_active(self, value: bool) -> None:
        self._active = value

    def set_update_handler(self, handler: UpdateHandler) -> None:
        """Attach a function that runs every frame for this object."""
        self.update_handler = handler

    def set_draw_handler(self, handler: DrawHandler) -> None:
        """Attach a function that draws this object on the screen."""
        self.draw_handler = handler

    def update(self, screen_size: ScreenSize) -> None:
        """Run this object's update handler, if it has one."""
        if self.update_handler is not None:
            self.update_handler(self, screen_size)

    def draw(self, surface: "pygame.Surface") -> None:
        """Run this object's draw handler, if it has one."""
        if self.draw_handler is not None:
            self.draw_handler(self, surface)

    def get_rect(self) -> "pygame.Rect":
        """Return this object's position and size as a Pygame rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
