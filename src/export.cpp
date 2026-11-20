#include "export.h"
#include "triangles.h"

#include <cstdint>
#include <vector>

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

std::vector<triangle_s_t> scene;

extern "C" void framebuffer_clear(uint32_t color);
extern "C" void Zbuffer_clear();

extern "C" void camera_update();
extern "C" triangle_t transform_triangle(triangle_t triangle);
extern "C" int project_triangle(triangle_t triangle, triangle2_t output[2]);

extern "C" void rasterize_triangle(triangle2_t triangle, uint32_t color);

extern "C" uint32_t* framebuffer_get_pixels();

EXPORT uint32_t* draw_frame(){
    framebuffer_clear(0xFF000000);
    Zbuffer_clear();

    camera_update();

    scene.clear();
    scene.push_back({
        {
            {-1.0f, -1.0f, 5.0f},
            { 1.0f, -1.0f, 5.0f},
            { 0.0f,  1.0f, 5.0f}
        },
        0xFFFF0000
    });

    triangle2_t projected[2];
    triangle_t triangle;
    for(auto triangle_s : scene){
        triangle = triangle_s.triangle;

        triangle = transform_triangle(triangle);

        int count = project_triangle(triangle, projected);

        for (int i = 0; i < count; i++) {
            rasterize_triangle(projected[i], triangle_s.color);
        }
    }

    return framebuffer_get_pixels();
}