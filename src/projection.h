#pragma once

#include "pos.h"

typedef struct {
    position_t position;
    rotation_t rotation;

    float near_plane;
    float focal_length;
} camera_t;

extern camera_t camera;
