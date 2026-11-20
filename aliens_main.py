#------------- IMPORTS -----------------
import loader

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

SCREEN_WIDTH = 100
SCREEN_HEIGHT = 100

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


def handle_keydown(app: GameApp, event) -> None:
    player = app.get_object("player")
    bullet = app.get_object("bullet")

    if event.key == pygame.K_RIGHT:
        player.vx = PLAYER_SPEED
    elif event.key == pygame.K_LEFT:
        player.vx = -PLAYER_SPEED

    if event.key == pygame.K_SPACE:
        if not bullet.active:
            bullet.active = True
            bullet.x = player.x + player.width / 2
            bullet.y = player.y
            app.play_sound('fire_laser')


def is_colliding(first: GameObject, second: GameObject) -> bool:
    return (
        first.x < second.x + second.width
        and first.x + first.width > second.x
        and first.y < second.y + second.height
        and first.y + first.height > second.y
    )

def handle_keyup(app: GameApp, event) -> None:
    player = app.get_object("player")

    if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
        player.vx = 0

def screen_draw_handler(obj: GameObject, surface):
    surface = pygame.image.frombuffer(obj.buffer, (SCREEN_WIDTH, SCREEN_HEIGHT), "ARGB")
    pygame.display.flip()

def buffer_render(obj: GameObject):
    loader.renderer.draw_frame()

def build_app() -> GameApp:
    app = GameApp(width=1000, height=600, title="UFO Shooter", bg_color=(255, 255, 255))
    
    screen = GameObject(0, 0, SCREEN_HEIGHT, SCREEN_HEIGHT)
    
    screen.set_draw_handler(screen_draw_handler)
    app.add_object("Screen", screen)

    return app


if __name__ == "__main__":
    build_app().on_execute()
