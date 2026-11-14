from __future__ import annotations

from .sprite_tools import Animation, DirectionalAnimation

try:
    import pygame
except ModuleNotFoundError:
    from .pygame_stub import pygame

from .game_object import GameObject, ScreenSize


class SpriteObject(GameObject):
    """A game object that can display an image."""

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 50,
        height: int = 50,
        image_path: str | None = None,
    ) -> None:
        """Create an image object with a position, size, and optional image file."""
        super().__init__(x, y, width, height)
        self.directional_animation: DirectionalAnimation | None = None
        self.animation: Animation | DirectionalAnimation | None = None
        self.image: pygame.Surface | None = None
        self.image_path: str | None = None
        self.is_active: bool = True
        if image_path is not None:
            self.set_image(image_path)
        self.set_draw_handler(self.draw_handler)

    def set_image(self, image_path: str) -> None:
        """Load and resize an image for this object."""
        self.image_path = image_path
        try:
            image = pygame.image.load(image_path)
            try:
                image = image.convert_alpha()
            except pygame.error:
                pass
            self.image = pygame.transform.scale(image, (self.width, self.height))
        except (FileNotFoundError, pygame.error):
            self.image = None

    def update(self, screen_size: ScreenSize) -> None:
        """Run this sprite's update handler, if it has one."""
        if self.update_handler is not None:
            self.update_handler(self, screen_size)

    def set_animation(self, direction: str, reset_frame: bool = True) -> None:
        """Change this sprite's directional animation."""
        if self.directional_animation is not None:
            self.directional_animation.set_direction(direction, reset_frame)
        elif isinstance(self.animation, DirectionalAnimation):
            self.animation.set_direction(direction, reset_frame)
        else:
            raise ValueError("This sprite does not have a directional animation")

    def update_animation(self) -> None:
        """Move this sprite's animation to its next frame when ready."""
        if self.directional_animation is not None:
            self.directional_animation.update()
        elif self.animation is not None:
            self.animation.update()

    def _get_animation_frame(self) -> object | None:
        """Return the current animation frame, if this sprite has one."""
        if self.directional_animation is not None:
            return self.directional_animation.current_frame
        if self.animation is not None:
            return self.animation.current_frame
        return None

    def _draw_frame(self, frame: object, surface: "pygame.Surface") -> None:
        """Draw one animation frame or colour block."""
        if hasattr(frame, "blit") or hasattr(frame, "get_width"):
            surface.blit(frame, self.get_rect())
        else:
            self.color = frame
            pygame.draw.rect(surface, self.color, self.get_rect())

    def draw(self, surface: pygame.Surface) -> None:
        """Draw this sprite image, animation frame, or custom draw handler."""
        if self.draw_handler is not None:
            self.draw_handler(self, surface)
            return

        if not getattr(self, "active", True):
            return

        frame = self._get_animation_frame()
        if frame is not None:
            self._draw_frame(frame, surface)
        elif self.image is not None:
            surface.blit(self.image, self.get_rect())
