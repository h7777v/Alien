Year 8 Pygame Sprite Sheets

Files:
1. walking_dog_directional_64x64_4x4.png
   - Transparent PNG
   - Frame size: 64 x 64
   - Layout: 4 columns x 4 rows
   - Rows:
     row 0 = down
     row 1 = left
     row 2 = right
     row 3 = up
   - Frames per direction: 4

2. helicopter_rotor_sequence_96x64_4frames.png
   - Transparent PNG
   - Frame size: 96 x 64
   - Layout: 4 columns x 1 row
   - Row 0 = rotor animation
   - Frames: 4

Suggested course folder:
images/sprites/

Suggested helper calls:
dog_frames = load_directional_sprite_sheet(
    "images/sprites/walking_dog_directional_64x64_4x4.png",
    frame_width=64,
    frame_height=64,
    frame_count=4,
    directions=["down", "left", "right", "up"],
    scale=1
)

helicopter_frames = load_sprite_sheet_row(
    "images/sprites/helicopter_rotor_sequence_96x64_4frames.png",
    row=0,
    frame_width=96,
    frame_height=64,
    frame_count=4,
    scale=1
)

These sprites were generated for classroom/course use.
