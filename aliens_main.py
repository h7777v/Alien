#------------- IMPORTS -----------------
import loader
import ctypes

import game_framework.sprite_tools
from game_framework.sprite_tools import load_directional_sprite_sheet, load_sprite_sheet_row, DirectionalAnimation
from game_framework import SpriteObject

try:
    import pygame
except ModuleNotFoundError:
    from game_framework.pygame_stub import pygame

from game_framework.app import GameApp
from game_framework.game_object import GameObject, ScreenSize
from game_framework.rectangle import Rectangle
from game_framework import sprite_tools
from game_framework.sprite_tools import Animation

#------

PLAYER_SPEED = 15
UFO_SPEED = 8
BULLET_SPEED = -20

BACKGROUND_IMAGE = "images/space_background.jpg"
PLAYER_SPRITE_PATH = "images/sprites/fighter_sprite_frames.png"
UFO_SPRITE_PATH = "images/sprites/ufo_sprite_1_frames.png"
LASER_SOUND_FILE = "sounds/laser_sound.mp3"

# -----

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

craterDifficulty = 10_000_000_000_000_000
seed = 12345

# keys

W = False
A = False
S = False
D = False

# Adjust these to match the actual sprite sheet image sizes.
PLAYER_FRAME_WIDTH = 72
PLAYER_FRAME_HEIGHT = 72
PLAYER_FRAME_COUNT = 3
PLAYER_DIRECTIONS = ["right", "idle", "left"]


def bullet_update_handler(obj:GameObject, scree_size:ScreenSize) -> None:
    if not obj.active:
        return

    obj.y = obj.y + obj.vy
    if obj.y <= 0:
        obj.active = False

def draw_bullet_handler(obj: GameObject, surface):
    if not obj.active:
        return

    rect = obj.get_rect()
    pygame.draw.rect(surface, obj.color, rect)

def ufo_update_handler(ufo:SpriteObject, scree_size:ScreenSize) -> None:
    ufo.y = ufo.y + ufo.vy

    if ufo.y + ufo.height > scree_size[1]:
        ufo.x = random.randint(0,scree_size[0] - ufo.width)
        ufo.y = 0
    ufo.update_animation()
    app = ufo.app

    bullet = app.get_object('bullet')
    if is_colliding(ufo, bullet):
        ufo.x =  random.randint(0,scree_size[0] - ufo.width)
        ufo.y = 0
        bullet.active = False


def player_update_handler(player: SpriteObject, screen_size: ScreenSize) -> None:
    player.x = player.x + player.vx

    # Keep the player inside the screen.
    player.x = max(0, min(player.x, screen_size[0] - player.width))

    # Animate only while moving.
    if player.vx > 0:
        player.set_animation("right", True)
        player.update_animation()
    elif player.vx < 0:
        player.set_animation("left", True)
        player.update_animation()
    else:
        player.set_animation("idle", True)


# important stuff

def handle_keydown(app: GameApp, event) -> None:
    global W, A, S, D
    if event.key == pygame.K_w or event.key == pygame.K_UP:
        W = True
    elif event.key == pygame.K_a or event.key == pygame.K_RIGHT:
        A = True
    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
        S = True
    elif event.key == pygame.K_d or event.key == pygame.K_LEFT:
        D = True

def handle_keyup(app: GameApp, event) -> None:
    global W, A, S, D
    if event.key == pygame.K_w or event.key == pygame.K_UP:
        W = False
    elif event.key == pygame.K_a or event.key == pygame.K_RIGHT:
        A = False
    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
        S = False
    elif event.key == pygame.K_d or event.key == pygame.K_LEFT:
        D = False

def update_screen(obj: GameObject, _) -> None:
    print(obj.app.clock.get_fps())
    global W, A, S, D
    obj.cpx += 2 * W
    obj.cpx -= 2 * S
    obj.cry += 0.1 * D
    obj.cry -= 0.1 * A
    loader.renderer.update_camera(obj.cpx, obj.cpy, obj.cpz, obj.cry, obj.crp, obj.crr) # pyright: ignore[reportAttributeAccessIssue]

def screen_draw_handler(obj: GameObject, surface) -> None:
    surface.blit(
        pygame.image.frombuffer(
            memoryview(
                ctypes.cast(
                    loader.renderer.draw_frame(),
                    ctypes.POINTER(ctypes.c_uint32 * (SCREEN_WIDTH * SCREEN_HEIGHT)),
                ).contents
            ).cast("B"),
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            "BGRA",
        ),
        (obj.x, obj.y),
    )

def build_app() -> GameApp:
    app = GameApp(width=1000, height=600, title="UFO Shooter", bg_color=(255, 255, 255))
    screen = GameObject(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

    loader.renderer.terrain_init(seed, craterDifficulty)

    if not loader.renderer.framebuffer_init(SCREEN_WIDTH, SCREEN_HEIGHT):
        raise RuntimeError("Failed to initialise framebuffer (OOM)")
    if not loader.renderer.Zbuffer_init(SCREEN_WIDTH, SCREEN_HEIGHT):
        loader.renderer.framebuffer_destroy()
        raise RuntimeError("Failed to initialise Z-buffer (OOM)")

    screen.set_draw_handler(screen_draw_handler)
    screen.set_update_handler(update_screen)

    loader.renderer.cpu_init()
    loader.renderer.init_camera(ctypes.c_float(500.0))

    screen.cpx = 0 # pyright: ignore[reportAttributeAccessIssue]
    screen.cpy = 50 # pyright: ignore[reportAttributeAccessIssue]
    screen.cpz = 0 # pyright: ignore[reportAttributeAccessIssue]
    screen.cry = 0 # pyright: ignore[reportAttributeAccessIssue]
    screen.crp = -0.3 # pyright: ignore[reportAttributeAccessIssue]
    screen.crr = 0 # pyright: ignore[reportAttributeAccessIssue]

    app.add_object("Screen", screen)

    app.set_keydown_handler(handle_keydown)
    app.set_keyup_handler(handle_keyup)

    return app

if __name__ == "__main__":
    build_app().on_execute()
