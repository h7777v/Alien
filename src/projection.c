#include <math.h>
#include <immintrin.h>

#include "cpu.h"

#include "projection.h"
#include "triangles.h"
#include "rasterization.h"
#include "framebuffer.h"

camera_t camera = {0};

void camera_update(){
    camera.cy = cosf(camera.rotation.yaw);
    camera.sy = sinf(camera.rotation.yaw);
    camera.cp = cosf(camera.rotation.pitch);
    camera.sp = sinf(camera.rotation.pitch);
    camera.cr = cosf(camera.rotation.roll);
    camera.sr = sinf(camera.rotation.roll);
}

vertex_t transform_vertex(vertex_t v){
    float t;

    v.x -= camera.position.x;
    v.y -= camera.position.y;
    v.z -= camera.position.z;

    t = camera.cy * v.x - camera.sy * v.z;
    v.z = camera.sy * v.x + camera.cy * v.z;
    v.x = t;

    t = camera.cp * v.y + camera.sp * v.z;
    v.z = -camera.sp * v.y + camera.cp * v.z;
    v.y = t;

    t = camera.cr * v.x + camera.sr * v.y;
    v.y = -camera.sr * v.x + camera.cr * v.y;
    v.x = t;

    return v;
}

triangle_t transform_triangle(triangle_t triangle){
    return (triangle_t){
        .a = transform_vertex(triangle.a),
        .b = transform_vertex(triangle.b),
        .c = transform_vertex(triangle.c)
    };
}

vertex2_t project_vertex(vertex_t vertex){
    vertex2_t vertex2;

    float dx = vertex.x;
    float dy = vertex.y;
    float dz = vertex.z;

    if(dz < camera.near_plane)return (vertex2_t){.x = INFINITY};

    float inv_dz = 1 / dz;

    vertex2.x = (framebuffer.width >> 1) + camera.focal_length * dx * inv_dz;
    vertex2.y = (framebuffer.height >> 1) - camera.focal_length * dy * inv_dz;
    vertex2.z = dz;

    return vertex2;
}

int project_triangle(triangle_t triangle, triangle2_t output[2]){
    vertex_t a = triangle.a;
    vertex_t b = triangle.b;
    vertex_t c = triangle.c;

    int ai = a.z >= camera.near_plane;
    int bi = b.z >= camera.near_plane;
    int ci = c.z >= camera.near_plane;

    if(!ai && !bi && !ci)return 0;

    if(ai && bi && ci){
        output[0] = (triangle2_t){
            project_vertex(a),
            project_vertex(b),
            project_vertex(c)
        };

        return 1;
    }

    int inside[3] = {ai, bi, ci};

    vertex_t input[3] = {
        triangle.a,
        triangle.b,
        triangle.c
    };

    vertex_t clipped[4];
    int count = 0;

    for(int i = 0; i < 3; i++){
        vertex_t a = input[i];
        vertex_t b = input[(i + 1) % 3];

        int a_inside = inside[i];
        int b_inside = inside[(i + 1) % 3];

        if(a_inside)clipped[count++] = a;

        if(a_inside != b_inside){
            float t = (camera.near_plane - a.z) / (b.z - a.z);

            clipped[count++] = (vertex_t){
                .x = a.x + t * (b.x - a.x),
                .y = a.y + t * (b.y - a.y),
                .z = camera.near_plane
            };
        }
    }

    if(count < 3)return 0;

    output[0] = (triangle2_t){
        .a = project_vertex(clipped[0]),
        .b = project_vertex(clipped[1]),
        .c = project_vertex(clipped[2])
    };

    if(count == 3)return 1;

    output[1] = (triangle2_t){
        .a = project_vertex(clipped[0]),
        .b = project_vertex(clipped[2]),
        .c = project_vertex(clipped[3])
    };

    return 2;
}

//vector stuff

void transform_triangles_avx2(const triangle_t* input, triangle_t* output, size_t count){
    const __m256 cy = _mm256_set1_ps(camera.cy);
    const __m256 sy = _mm256_set1_ps(camera.sy);
    const __m256 cp = _mm256_set1_ps(camera.cp);
    const __m256 sp = _mm256_set1_ps(camera.sp);
    const __m256 cr = _mm256_set1_ps(camera.cr);
    const __m256 sr = _mm256_set1_ps(camera.sr);

    const __m256 px = _mm256_set1_ps(camera.position.x);
    const __m256 py = _mm256_set1_ps(camera.position.y);
    const __m256 pz = _mm256_set1_ps(camera.position.z);

    const __m256 neg_sr = _mm256_sub_ps(_mm256_setzero_ps(), sr);
    const __m256 neg_sp = _mm256_sub_ps(_mm256_setzero_ps(), sp);

    size_t i = 0;

    for(; i + 8 <= count; i += 8){
        float x[24], y[24], z[24];

        for(int j = 0; j < 8; j++){
            x[j]      = input[i+j].a.x;
            x[j+8]    = input[i+j].b.x;
            x[j+16]   = input[i+j].c.x;

            y[j]      = input[i+j].a.y;
            y[j+8]    = input[i+j].b.y;
            y[j+16]   = input[i+j].c.y;

            z[j]      = input[i+j].a.z;
            z[j+8]    = input[i+j].b.z;
            z[j+16]   = input[i+j].c.z;
        }

        for(int j = 0; j < 3; j++){
            __m256 vx = _mm256_loadu_ps(&x[j*8]);
            __m256 vy = _mm256_loadu_ps(&y[j*8]);
            __m256 vz = _mm256_loadu_ps(&z[j*8]);

            vx = _mm256_sub_ps(vx, px);
            vy = _mm256_sub_ps(vy, py);
            vz = _mm256_sub_ps(vz, pz);

            __m256 t;

            t = _mm256_sub_ps(
                _mm256_mul_ps(cy, vx),
                _mm256_mul_ps(sy, vz)
            );

            vz = _mm256_add_ps(
                _mm256_mul_ps(sy, vx),
                _mm256_mul_ps(cy, vz)
            );

            vx = t;

            t = _mm256_add_ps(
                _mm256_mul_ps(cp, vy),
                _mm256_mul_ps(sp, vz)
            );

            vz = _mm256_add_ps(
                _mm256_mul_ps(neg_sp, vy),
                _mm256_mul_ps(cp, vz)
            );

            vy = t;

            t = _mm256_add_ps(
                _mm256_mul_ps(cr, vx),
                _mm256_mul_ps(sr, vy)
            );

            vy = _mm256_add_ps(
                _mm256_mul_ps(neg_sr, vx),
                _mm256_mul_ps(cr, vy)
            );

            vx = t;

            _mm256_storeu_ps(&x[j*8], vx);
            _mm256_storeu_ps(&y[j*8], vy);
            _mm256_storeu_ps(&z[j*8], vz);
        }

        for(int j = 0; j < 8; j++){
            output[i+j].a = (vertex_t){x[j], y[j], z[j]};
            output[i+j].b = (vertex_t){x[j+8], y[j+8], z[j+8]};
            output[i+j].c = (vertex_t){x[j+16], y[j+16], z[j+16]};
        }
    }

    for(; i < count; i++){
        output[i].a = transform_vertex(input[i].a);
        output[i].b = transform_vertex(input[i].b);
        output[i].c = transform_vertex(input[i].c);
    }
}

void transform_triangles_avx2_strided(const void* input, size_t stride, triangle_t* output, size_t count){
    const __m256 cy = _mm256_set1_ps(camera.cy);
    const __m256 sy = _mm256_set1_ps(camera.sy);
    const __m256 cp = _mm256_set1_ps(camera.cp);
    const __m256 sp = _mm256_set1_ps(camera.sp);
    const __m256 cr = _mm256_set1_ps(camera.cr);
    const __m256 sr = _mm256_set1_ps(camera.sr);

    const __m256 nsp = _mm256_set1_ps(-camera.sp);
    const __m256 nsr = _mm256_set1_ps(-camera.sr);

    const __m256 px = _mm256_set1_ps(camera.position.x);
    const __m256 py = _mm256_set1_ps(camera.position.y);
    const __m256 pz = _mm256_set1_ps(camera.position.z);

    size_t i = 0;

    for(; i + 8 <= count; i += 8){
        float x[24], y[24], z[24];

        for(int j = 0; j < 8; j++){
            const triangle_t* t = (const triangle_t*)((const uint8_t*)input + (i + j) * stride);

            x[j]      = t->a.x;
            x[j + 8]  = t->b.x;
            x[j + 16] = t->c.x;

            y[j]      = t->a.y;
            y[j + 8]  = t->b.y;
            y[j + 16] = t->c.y;

            z[j]      = t->a.z;
            z[j + 8]  = t->b.z;
            z[j + 16] = t->c.z;
        }

        for(int j = 0; j < 3; j++){
            __m256 vx = _mm256_loadu_ps(&x[j * 8]);
            __m256 vy = _mm256_loadu_ps(&y[j * 8]);
            __m256 vz = _mm256_loadu_ps(&z[j * 8]);

            vx = _mm256_sub_ps(vx, px);
            vy = _mm256_sub_ps(vy, py);
            vz = _mm256_sub_ps(vz, pz);

            __m256 t;

            t = _mm256_sub_ps(_mm256_mul_ps(cy, vx), _mm256_mul_ps(sy, vz));
            vz = _mm256_add_ps(_mm256_mul_ps(sy, vx), _mm256_mul_ps(cy, vz));
            vx = t;

            t = _mm256_add_ps(_mm256_mul_ps(cp, vy), _mm256_mul_ps(sp, vz));
            vz = _mm256_add_ps(_mm256_mul_ps(nsp, vy), _mm256_mul_ps(cp, vz));
            vy = t;

            t = _mm256_add_ps(_mm256_mul_ps(cr, vx), _mm256_mul_ps(sr, vy));
            vy = _mm256_add_ps(_mm256_mul_ps(nsr, vx), _mm256_mul_ps(cr, vy));
            vx = t;

            _mm256_storeu_ps(&x[j * 8], vx);
            _mm256_storeu_ps(&y[j * 8], vy);
            _mm256_storeu_ps(&z[j * 8], vz);
        }

        for(int j = 0; j < 8; j++){
            output[i + j].a = (vertex_t){x[j], y[j], z[j]};
            output[i + j].b = (vertex_t){x[j + 8], y[j + 8], z[j + 8]};
            output[i + j].c = (vertex_t){x[j + 16], y[j + 16], z[j + 16]};
        }
    }

    for(; i < count; i++){
        const triangle_t* t = (const triangle_t*)((const uint8_t*)input + i * stride);

        output[i] = transform_triangle(*t);
    }
}