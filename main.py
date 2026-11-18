import loader

try:
    import pygame
except ModuleNotFoundError:
    from game_framework.pygame_stub import pygame

from game_framework.app import GameApp

import pygame
from game_framework import GameApp, GameObject


class CFrameView(GameObject):
    def __init__(self, x, y, w, h, get_frame, scale=1):
        super().__init__(x, y, w * scale, h * scale)
        self.size = (w, h)
        self.get_frame = get_frame
        self._dst = pygame.Surface((self.width, self.height))

    def draw(self, surface):
        src = pygame.image.frombuffer(self.get_frame(), self.size, "ARGB") # I think TODO: double check colour format
        pygame.transform.scale(src, self._dst.get_size(), self._dst)
        surface.blit(self._dst, (self.x, self.y))

def build_app() -> GameApp:
    app = GameApp(
        title="Everlands"
    )

    return app

if __name__ == "__main__":
    build_app().on_execute()