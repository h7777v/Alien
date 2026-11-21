#pragma once

#include <stdint.h>

typedef struct {
    float x;
    float y;
    float z;
} vertex2_t;

typedef struct {
    vertex2_t a;
    vertex2_t b;
    vertex2_t c;
} triangle2_t;

void rasterize_triangle_barycentric(triangle2_t triangle, uint32_t color);
void rasterize_triangle_scanline(triangle2_t triangle, uint32_t color);