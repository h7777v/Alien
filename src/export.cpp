#include "export.h"
#include "triangles.h"
#include "terrain.h"
#include "lighting.h"

#include "cpu.h"

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

typedef struct {
    triangle_light_t* triangles;
    uint64_t triangle_count;

    int32_t chunk_x;
    int32_t chunk_z;

    int detail;
} chunks_data;

chunks_data terrain_chunks[3][3];

float heightmap_buffer[1048576];
std::vector<triangle_s_t> scene;

triangle_t* transformed = nullptr;

extern "C" void framebuffer_clear(uint32_t color);
extern "C" void Zbuffer_clear();

extern "C" void camera_update();
extern "C" triangle_t transform_triangle(triangle_t triangle);
extern "C" int project_triangle(triangle_t triangle, triangle2_t output[2]);

extern "C" void rasterize_triangle_scanline(triangle2_t triangle, uint32_t color);

extern "C" uint32_t* framebuffer_get_pixels();

extern "C" void transform_triangles_avx2_strided(const void* input, size_t stride, triangle_t* output, size_t count);

static inline int is_backface(triangle_t triangle){
    float ax = triangle.b.x - triangle.a.x;
    float ay = triangle.b.y - triangle.a.y;
    float az = triangle.b.z - triangle.a.z;

    float bx = triangle.c.x - triangle.a.x;
    float by = triangle.c.y - triangle.a.y;
    float bz = triangle.c.z - triangle.a.z;

    float nx = ay * bz - az * by;
    float ny = az * bx - ax * bz;
    float nz = ax * by - ay * bx;

    return nx * triangle.a.x + ny * triangle.a.y + nz * triangle.a.z >= 0.0f;
}

EXPORT uint32_t* draw_frame(){
    framebuffer_clear(0xFF000000);
    Zbuffer_clear();

    camera_update();

    if(terrain_chunks[1][1].triangles == nullptr){
        terrain_chunks[1][1].triangles = new triangle_light_t[2097152];
        terrain_chunks[1][1].triangle_count = 2097152;

        generate_chunk(
            terrain_chunks[1][1].chunk_x,
            terrain_chunks[1][1].chunk_z,
            1,
            heightmap_buffer
        );

        triangulate_chunk(
            heightmap_buffer,
            1,
            terrain_chunks[1][1].triangles
        );
    }

    triangle2_t projected[2];
    triangle_t triangle;

    uint64_t count = terrain_chunks[1][1].triangle_count;

    if(cpu_features.avx2){
        if(transformed == nullptr){
            transformed = new triangle_t[terrain_chunks[1][1].triangle_count];
        }

        transform_triangles_avx2_strided(
            terrain_chunks[1][1].triangles,
            sizeof(triangle_light_t),
            transformed,
            terrain_chunks[1][1].triangle_count
        );

        for(uint64_t i = 0; i < count; i++){
            triangle_light_t& triangle_l = terrain_chunks[1][1].triangles[i];

            triangle = transformed[i];

            if(is_backface(triangle))continue;

            int projected_count = project_triangle(triangle, projected);

            for(int j = 0; j < projected_count; j++){
                rasterize_triangle_scanline(
                    projected[j],
                    apply_brightness(0xFF77736C, triangle_l.brightness)
                );
            }
        }
    }else{
        for(uint64_t i = 0; i < count; i++){
            triangle_light_t& triangle_l = terrain_chunks[1][1].triangles[i];

            triangle = transform_triangle(triangle_l.triangle);

            if(is_backface(triangle))continue;

            int projected_count = project_triangle(triangle, projected);

            for(int j = 0; j < projected_count; j++){
                rasterize_triangle_scanline(
                    projected[j],
                    apply_brightness(0xFF77736C, triangle_l.brightness)
                );
            }
        }
    }

    for(auto triangle_s : scene){
        triangle = triangle_s.triangle;

        triangle = transform_triangle(triangle);

        int count = project_triangle(triangle, projected);

        for(int i = 0; i < count; i++){
            rasterize_triangle_scanline(projected[i], triangle_s.color);
        }
    }

    return framebuffer_get_pixels();
}