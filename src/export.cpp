#include "export.h"
#include "triangles.h"

#include <cstdint>

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

extern "C" void framebuffer_clear(uint32_t color);
extern "C" void Zbuffer_clear();

extern "C" void camera_update();
extern "C" triangle_t transform_triangle(triangle_t triangle);
extern "C" int project_triangle(triangle_t triangle, triangle2_t output[2]);

extern "C" void rasterize_triangle(triangle2_t triangle, uint32_t color);