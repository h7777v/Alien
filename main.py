import loader

try:
    import pygame
except ModuleNotFoundError:
    from game_framework.pygame_stub import pygame

from game_framework.app import GameApp

def build_app() -> GameApp:
    app = GameApp(
        title="Everlands"
    )

    return app

if __name__ == "__main__":
    build_app().on_execute()