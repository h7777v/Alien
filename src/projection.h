#pragma once

#include "rasterization.h"
#include "triangles.h"
#include "pos.h"

#include "export.h"

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

EXPORT void update_camera(float x, float y, float z, float yaw, float pitch, float roll){
    camera.position.x = x;
    camera.position.y = y;
    camera.position.z = z;
    camera.rotation.yaw = yaw;
    camera.rotation.pitch = pitch;
    camera.rotation.roll = roll;
}

EXPORT void init_camera(float fl){
    camera.focal_length = fl;
    camera.near_plane = 0.1f;
}