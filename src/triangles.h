#pragma once

#include <stdint.h>

typedef struct {
    float x;
    float y;
    float z;
} vertex_t;

typedef struct {
    vertex_t a;
    vertex_t b;
    vertex_t c;
} triangle_t;

typedef struct {
    triangle_t triangle;
    uint32_t color;
} triangle_s_t;