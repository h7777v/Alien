from __future__ import annotations

try:
    import pygame
except ModuleNotFoundError:
    from .pygame_stub import pygame

from .game_object import ScreenSize
from .sprite_object import SpriteObject


class Player(SpriteObject):
    """A sprite object with simple keyboard-style movement helpers."""

    def __init__(
        self,
        x: int = 100,
        y: int = 100,
        width: int = 60,
        height: int = 60,
        image_path: str | None = None,
        speed: int = 5,
    ) -> None:
        """Create a player with a position, size, optional image, and speed."""
        super().__init__(x, y, width, height, image_path)
        self.speed = speed

    def move_left(self) -> None:
        """Set the player to move left."""
        self.vx = -self.speed

    def move_right(self) -> None:
        """Set the player to move right."""
        self.vx = self.speed

    def move_up(self) -> None:
        """Set the player to move up."""
        self.vy = -self.speed

    def move_down(self) -> None:
        """Set the player to move down."""
        self.vy = self.speed

    def stop_x(self) -> None:
        """Stop the player's horizontal movement."""
        self.vx = 0

    def stop_y(self) -> None:
        """Stop the player's vertical movement."""
        self.vy = 0

    def stop(self) -> None:
        """Stop the player moving in all directions."""
        self.stop_x()
        self.stop_y()

    def update(self, screen_size: ScreenSize) -> None:
        """Move the player and keep it inside the screen."""
        if self.update_handler is not None:
            self.update_handler(self, screen_size)
            return

        self.x += self.vx
        self.y += self.vy

        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0
        if self.x + self.width > screen_size[0]:
            self.x = screen_size[0] - self.width
        if self.y + self.height > screen_size[1]:
            self.y = screen_size[1] - self.height

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw the player image or a simple rectangle."""
        if self.draw_handler is not None:
            self.draw_handler(self, surface)
        elif self.image is not None:
            surface.blit(self.image, (self.x, self.y))
        else:
            rect = pygame.Rect(self.x, self.y, self.width, self.height)
            pygame.draw.rect(surface, (60, 120, 220), rect)
