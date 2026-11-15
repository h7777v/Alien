#pragma once

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