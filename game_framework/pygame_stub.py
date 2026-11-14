from types import SimpleNamespace


class PygameError(Exception):
    pass


class Color(tuple):
    def __new__(cls, *channels: int | tuple[int, ...] | list[int]) -> "Color":
        if len(channels) == 1 and isinstance(channels[0], (tuple, list)):
            channels = tuple(channels[0])
        return super().__new__(cls, channels)


class Rect:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class _Surface:
    def __init__(self, size: tuple[int, int] = (0, 0)) -> None:
        self.size = size
        self.fills = []
        self.blit_calls = []

    def fill(self, color: tuple[int, int, int]) -> None:
        self.fills.append(color)

    def blit(self, image: object, position: tuple[int, int] | Rect) -> None:
        self.blit_calls.append((image, position))

    def get_width(self) -> int:
        return self.size[0]

    def get_height(self) -> int:
        return self.size[1]

    def get_size(self) -> tuple[int, int]:
        return self.size

    def copy(self) -> "_Surface":
        return _Surface(self.size)

    def subsurface(self, rect: Rect) -> "_Surface":
        return _Surface((rect.width, rect.height))


class _Image(_Surface):
    def convert_alpha(self) -> "_Image":
        return self

    def convert(self) -> "_Image":
        return self


class _RenderedText(_Surface):
    def __init__(self, text: str = "", size: tuple[int, int] = (0, 0)) -> None:
        super().__init__(size)
        self.text = text


class _Font:
    def __init__(self, _name: str | None, size: int) -> None:
        self.size = size

    def render(self, text: str, _antialias: bool, _color: tuple[int, int, int]) -> _RenderedText:
        width = max(len(text), 1) * max(self.size // 2, 1)
        return _RenderedText(text=text, size=(width, self.size))


class _Clock:
    def tick(self, fps: int) -> int:
        return fps


class _Sound:
    def __init__(self, path: str) -> None:
        self.path = path
        self.play_count = 0
        self.volume = 1.0

    def set_volume(self, volume: float) -> None:
        self.volume = volume

    def play(self) -> "_Sound":
        self.play_count += 1
        return self


class _Music:
    def __init__(self) -> None:
        self.path = ""
        self.volume = 1.0
        self.play_calls = []
        self.stop_count = 0

    def load(self, path: str) -> None:
        self.path = path

    def set_volume(self, volume: float) -> None:
        self.volume = volume

    def play(self, loops: int = 0) -> None:
        self.play_calls.append(loops)

    def stop(self) -> None:
        self.stop_count += 1


class _Mixer:
    def __init__(self) -> None:
        self.initialized = False
        self.music = _Music()

    def init(self) -> None:
        self.initialized = True

    def get_init(self) -> tuple[int, int, int] | None:
        if self.initialized:
            return (44100, -16, 2)
        return None

    def Sound(self, path: str) -> _Sound:
        return _Sound(path)


def _set_mode(size: tuple[int, int]) -> _Surface:
    return _Surface(size)


def _set_caption(title: str) -> str:
    return title


def _flip() -> None:
    return None


def _get_events() -> list[object]:
    return []


def _draw_rect(
    surface: _Surface,
    color: tuple[int, int, int],
    rect: Rect,
) -> tuple[_Surface, tuple[int, int, int], Rect]:
    return surface, color, rect


def _load_image(_path: str) -> _Image:
    return _Image()


def _scale_image(image: _Surface, size: tuple[int, int]) -> _Surface:
    image.size = size
    return image


pygame = SimpleNamespace(
    QUIT="QUIT",
    KEYDOWN="KEYDOWN",
    KEYUP="KEYUP",
    SRCALPHA="SRCALPHA",
    K_RIGHT="K_RIGHT",
    K_LEFT="K_LEFT",
    K_UP="K_UP",
    K_DOWN="K_DOWN",
    K_w="K_w",
    K_a="K_a",
    K_s="K_s",
    K_d="K_d",
    Rect=Rect,
    Surface=_Surface,
    error=PygameError,
    init=lambda: None,
    quit=lambda: None,
    time=SimpleNamespace(Clock=_Clock),
    mixer=_Mixer(),
    display=SimpleNamespace(set_mode=_set_mode, set_caption=_set_caption, flip=_flip),
    event=SimpleNamespace(get=_get_events),
    draw=SimpleNamespace(rect=_draw_rect),
    font=SimpleNamespace(Font=_Font),
    image=SimpleNamespace(load=_load_image),
    transform=SimpleNamespace(scale=_scale_image),
)
