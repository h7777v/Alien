from __future__ import annotations

try:
    import pygame
except ModuleNotFoundError:
    from .pygame_stub import pygame


def scale_surface(
    surface: "pygame.Surface",
    scale: float | None = None,
    width: int | None = None,
    height: int | None = None,
) -> "pygame.Surface":
    """Return a resized surface using simple classroom-friendly options."""
    if scale is None and width is None and height is None:
        return surface

    current_width = surface.get_width()
    current_height = surface.get_height()

    if scale is not None:
        new_width = int(current_width * scale)
        new_height = int(current_height * scale)
    elif width is not None and height is not None:
        new_width = int(width)
        new_height = int(height)
    elif width is not None:
        new_width = int(width)
        new_height = int(current_height * (new_width / current_width))
    else:
        new_height = int(height)
        new_width = int(current_width * (new_height / current_height))

    return pygame.transform.scale(surface, (new_width, new_height))


def load_image(
    path: str,
    scale: float | None = None,
    width: int | None = None,
    height: int | None = None,
) -> "pygame.Surface":
    """Load one image file and optionally resize it.

    Example:
        player_image = load_image("images/player.png", scale=2)
    """
    image = pygame.image.load(path)
    try:
        image = image.convert_alpha()
    except pygame.error:
        try:
            image = image.convert()
        except pygame.error:
            pass

    return scale_surface(image, scale=scale, width=width, height=height)


def load_sprite_sheet_row(
    path: str,
    row: int,
    frame_width: int,
    frame_height: int,
    frame_count: int,
    scale: float | None = None,
    width: int | None = None,
    height: int | None = None,
) -> list["pygame.Surface"]:
    """Load one row of animation frames from a sprite sheet.

    Rows are zero-indexed, so row 0 is the first row.

    Example:
        walk_frames = load_sprite_sheet_row("images/player.png", 0, 32, 32, 4)
    """
    if frame_width <= 0:
        raise ValueError("frame_width must be positive")
    if frame_height <= 0:
        raise ValueError("frame_height must be positive")
    if frame_count <= 0:
        raise ValueError("frame_count must be positive")
    if row < 0:
        raise ValueError("row must be zero or positive")

    sprite_sheet = load_image(path)
    frames = []

    for frame_index in range(frame_count):
        x = frame_index * frame_width
        y = row * frame_height
        frame_rect = pygame.Rect(x, y, frame_width, frame_height)
        frame = sprite_sheet.subsurface(frame_rect).copy()
        frame = scale_surface(frame, scale=scale, width=width, height=height)
        frames.append(frame)

    return frames


def load_directional_sprite_sheet(
    path: str,
    frame_width: int,
    frame_height: int,
    frame_count: int,
    directions: list[str] | tuple[str, ...] | None = None,
    scale: float | None = None,
    width: int | None = None,
    height: int | None = None,
) -> dict[str, list["pygame.Surface"]]:
    """Load a sprite sheet where each movement direction is stored on one row.

    Example:
        frames = load_directional_sprite_sheet("images/player.png", 32, 32, 4)
        right_frames = frames["right"]
    """
    if directions is None:
        directions = ["down", "left", "right", "up"]

    if len(directions) == 0:
        raise ValueError("directions must not be empty")

    for direction in directions:
        if not isinstance(direction, str):
            raise ValueError("direction names must be strings")

    frames_by_direction = {}
    for row, direction in enumerate(directions):
        frames_by_direction[direction] = load_sprite_sheet_row(
            path,
            row,
            frame_width,
            frame_height,
            frame_count,
            scale=scale,
            width=width,
            height=height,
        )

    return frames_by_direction


class Animation:
    """Manage simple frame timing for one list of animation frames."""

    def __init__(self, frames: list[object], frames_per_change: int = 6) -> None:
        """Create an animation from a list of frames."""
        if len(frames) == 0:
            raise ValueError("frames must not be empty")
        if frames_per_change <= 0:
            raise ValueError("frames_per_change must be positive")

        self.frames = frames
        self.frames_per_change = frames_per_change
        self.current_frame_index = 0
        self.frame_counter = 0

    @property
    def current_frame(self) -> object:
        """Return the frame that should be shown now."""
        return self.frames[self.current_frame_index]

    def update(self) -> None:
        """Move to the next animation frame when enough updates have passed."""
        self.frame_counter += 1
        if self.frame_counter >= self.frames_per_change:
            self.frame_counter = 0
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)

    def reset(self) -> None:
        """Restart the animation from the first frame."""
        self.current_frame_index = 0
        self.frame_counter = 0


class DirectionalAnimation:
    """Manage frame timing when each direction has its own frame list."""

    def __init__(
        self,
        frames_by_direction: dict[str, list[object]],
        starting_direction: str = "right",
        frames_per_change: int = 6,
    ) -> None:
        """Create an animation with a separate frame list for each direction."""
        if len(frames_by_direction) == 0:
            raise ValueError("frames_by_direction must not be empty")
        if frames_per_change <= 0:
            raise ValueError("frames_per_change must be positive")

        for direction, frames in frames_by_direction.items():
            if not isinstance(direction, str):
                raise ValueError("direction names must be strings")
            if len(frames) == 0:
                raise ValueError("each direction must have at least one frame")

        self.frames_by_direction = frames_by_direction
        if starting_direction in frames_by_direction:
            self.direction = starting_direction
        else:
            self.direction = next(iter(frames_by_direction))
        self.frames_per_change = frames_per_change
        self.current_frame_index = 0
        self.frame_counter = 0

    @property
    def current_frame(self) -> object:
        """Return the current frame for the current direction."""
        return self.frames_by_direction[self.direction][self.current_frame_index]

    def set_direction(self, direction: str, reset_frame: bool = True) -> None:
        """Change which direction's animation frames are being used."""
        if direction not in self.frames_by_direction:
            raise ValueError("direction must exist in frames_by_direction")

        if direction != self.direction:
            self.direction = direction
            if reset_frame:
                self.reset()

    def update(self) -> None:
        """Move to the next frame for the current direction."""
        frames = self.frames_by_direction[self.direction]
        self.frame_counter += 1
        if self.frame_counter >= self.frames_per_change:
            self.frame_counter = 0
            self.current_frame_index = (self.current_frame_index + 1) % len(frames)

    def reset(self) -> None:
        """Restart the current direction's animation from the first frame."""
        self.current_frame_index = 0
        self.frame_counter = 0
