#include <math.h>

#include "rasterization.h"
#include "framebuffer.h"
#include "Zbuffer.h"

//The barycentric rasterizer

typedef struct {
    float min_x;
    float max_x;
    float min_y;
    float max_y;
} bounding_box_t;

static inline float edge_function(vertex2_t vert1, vertex2_t vert2, vertex2_t point){
    return (vert2.x - vert1.x) * (point.y - vert1.y) - (vert2.y - vert1.y) * (point.x - vert1.x);
}

static inline float winding_function(triangle2_t triangle){
    return edge_function(triangle.a, triangle.b, triangle.c);
}

static inline bounding_box_t bounding_box(triangle2_t triangle){
    bounding_box_t box;
    box.max_x = fmaxf(fmaxf(triangle.a.x, triangle.b.x), triangle.c.x);
    box.max_y = fmaxf(fmaxf(triangle.a.y, triangle.b.y), triangle.c.y);
    box.min_x = fminf(fminf(triangle.a.x, triangle.b.x), triangle.c.x);
    box.min_y = fminf(fminf(triangle.a.y, triangle.b.y), triangle.c.y);
    return box;
}

static inline bounding_box_t bounding_box_clamp(bounding_box_t box){
    if(box.min_x < 0.0f) box.min_x = 0.0f;
    if(box.min_y < 0.0f) box.min_y = 0.0f;

    if(box.max_x > (float)(framebuffer.width - 1))box.max_x = (float)(framebuffer.width - 1);

    if(box.max_y > (float)(framebuffer.height - 1))box.max_y = (float)(framebuffer.height - 1);

    if(box.min_x > box.max_x || box.min_y > box.max_y)return (bounding_box_t){0};

    return box;
}

void rasterize_triangle_barycentric(triangle2_t triangle, uint32_t color){
    float area = winding_function(triangle);
    if(area == 0)return;
    bounding_box_t box = bounding_box(triangle);
    box = bounding_box_clamp(box);
    
    int min_x = (int)ceilf(box.min_x - 0.5f);
    int max_x = (int)floorf(box.max_x - 0.5f);
    int min_y = (int)ceilf(box.min_y - 0.5f);
    int max_y = (int)floorf(box.max_y - 0.5f);

    float inv_area = 1.0f / area;

    for(int y = min_y; y <= max_y; y++) {
        for (int x = min_x; x <= max_x; x++) {
            vertex2_t p = {
                (float)x + 0.5f,
                (float)y + 0.5f
            };

            float w0 = edge_function(triangle.a, triangle.b, p);
            float w1 = edge_function(triangle.b, triangle.c, p);
            float w2 = edge_function(triangle.c, triangle.a, p);

            if (area > 0.0f) {
                if (w0 >= 0 && w1 >= 0 && w2 >= 0) {
                    float alpha = w1 * inv_area;
                    float beta = w2 * inv_area;
                    float gamma = w0 * inv_area;

                    float z =
                        alpha * triangle.a.z +
                        beta  * triangle.b.z +
                        gamma * triangle.c.z;

                    if(z >= Zbuffer_get_pixel(x, y))continue;
                    
                    Zbuffer_set_pixel(x, y, z);
                    framebuffer_set_pixel(x, y, color);
                }
            } else {
                if (w0 <= 0 && w1 <= 0 && w2 <= 0) {
                    float alpha = w1 * inv_area;
                    float beta = w2 * inv_area;
                    float gamma = w0 * inv_area;

                    float z =
                        alpha * triangle.a.z +
                        beta  * triangle.b.z +
                        gamma * triangle.c.z;

                    if(z >= Zbuffer_get_pixel(x, y))continue;
                    
                    Zbuffer_set_pixel(x, y, z);
                    framebuffer_set_pixel(x, y, color);
                }
            }
        }
    }
}

//The scanline rasterizer

typedef struct {
    float x;
    float z;
} scanline_point_t;

static inline scanline_point_t interpolate_edge(vertex2_t a, vertex2_t b, float y){
    float t = (y - a.y) / (b.y - a.y);

    return (scanline_point_t){
        a.x + (b.x - a.x) * t,
        a.z + (b.z - a.z) * t
    };
}

static inline void rasterize_scanline(int y, scanline_point_t left, scanline_point_t right, uint32_t color){
    if(left.x > right.x){
        scanline_point_t t = left;
        left = right;
        right = t;
    }

    int min_x = (int)fmaxf(ceilf(left.x - 0.5f), 0.0f);
    int max_x = (int)fminf(ceilf(right.x - 0.5f), (float)framebuffer.width);

    float dz = right.x != left.x ? (right.z - left.z) / (right.x - left.x) : 0.0f;
    float z = left.z + ((float)min_x + 0.5f - left.x) * dz;

    for(int x = min_x; x < max_x; x++){
        if(z < Zbuffer_get_pixel(x, y)){
            Zbuffer_set_pixel(x, y, z);
            framebuffer_set_pixel(x, y, color);
        }

        z += dz;
    }
}

void rasterize_triangle_scanline(triangle2_t triangle, uint32_t color){
    vertex2_t v[3] = {
        triangle.a,
        triangle.b,
        triangle.c
    };

    if(v[0].y > v[1].y){
        vertex2_t t = v[0];
        v[0] = v[1];
        v[1] = t;
    }

    if(v[1].y > v[2].y){
        vertex2_t t = v[1];
        v[1] = v[2];
        v[2] = t;
    }

    if(v[0].y > v[1].y){
        vertex2_t t = v[0];
        v[0] = v[1];
        v[1] = t;
    }

    if(v[0].y == v[2].y)return;

    int min_y = (int)fmaxf(ceilf(v[0].y - 0.5f), 0.0f);
    int max_y = (int)fminf(ceilf(v[2].y - 0.5f), (float)framebuffer.height);

    for(int y = min_y; y < max_y; y++){
        float py = (float)y + 0.5f;

        if(py < v[1].y){
            rasterize_scanline(y, interpolate_edge(v[0], v[2], py), interpolate_edge(v[0], v[1], py), color);
        }else{
            rasterize_scanline(y, interpolate_edge(v[0], v[2], py), interpolate_edge(v[1], v[2], py), color);
        }
    }
}