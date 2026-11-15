#pragma once

#include "rasterization.h"
#include "triangles.h"
#include "pos.h"

typedef struct {
    position_t position;
    rotation_t rotation;

    float cy;
    float sy;
    float cp;
    float sp;
    float cr;
    float sr;

    float near_plane;
    float focal_length;
} camera_t;

extern camera_t camera;

void camera_update();
triangle_t transform_triangle(triangle_t triangle);
int project_triangle(triangle_t triangle, triangle2_t output[2]);