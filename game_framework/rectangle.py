from __future__ import annotations

try:
    import pygame
except ModuleNotFoundError:
    from .pygame_stub import pygame

from .game_object import Color, GameObject, ScreenSize


class Rectangle(GameObject):
    """A simple rectangle object that can draw itself if no draw handler is set."""

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 80,
        height: int = 50,
        color: Color = (50, 120, 220),
    ) -> None:
        """Create a rectangle with a position, size, and colour."""
        super().__init__(x, y, width, height, color)

    def update(self, screen_size: ScreenSize) -> None:
        """Run this rectangle's update handler, if it has one."""
        if self.update_handler is not None:
            self.update_handler(self, screen_size)

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw this rectangle or run its custom draw handler."""
        if self.draw_handler is not None:
            self.draw_handler(self, surface)
        else:
            rect = self.get_rect()
            pygame.draw.rect(surface, self.color, rect)
