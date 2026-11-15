#include <math.h>

#include "projection.h"
#include "triangles.h"
#include "rasterization.h"
#include "framebuffer.h"

camera_t camera = {0};

vertex_t transform_vertex(vertex_t vertex){
    float x = vertex.x - camera.position.x;
    float y = vertex.y - camera.position.y;
    float z = vertex.z - camera.position.z;

    float cy = cosf(camera.rotation.yaw);
    float sy = sinf(camera.rotation.yaw);

    float cp = cosf(camera.rotation.pitch);
    float sp = sinf(camera.rotation.pitch);

    float cr = cosf(camera.rotation.roll);
    float sr = sinf(camera.rotation.roll);

    float tx = cy * x - sy * z;
    float tz = sy * x + cy * z;
    x = tx;
    z = tz;

    float ty = cp * y + sp * z;
    tz = -sp * y + cp * z;
    y = ty;
    z = tz;

    tx = cr * x + sr * y;
    ty = -sr * x + cr * y;
    x = tx;
    y = ty;

    return (vertex_t){
        .x = x,
        .y = y,
        .z = z
    };
}

vertex2_t project_vertex(vertex_t vertex){
    vertex2_t vertex2;

    float dx = vertex.x - camera.position.x;
    float dy = vertex.y - camera.position.y;
    float dz = vertex.z - camera.position.z;

    if(dz < camera.near_plane)return (vertex2_t){.x = INFINITY};

    vertex2.x = (framebuffer.width >> 1) + camera.focal_length * dx / dz;
    vertex2.y = (framebuffer.height >> 1) - camera.focal_length * dy / dz;
    vertex2.z = dz;

    return vertex2;
}

int project_triangle(triangle_t triangle, triangle2_t output[2]){
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

        int a_inside = a.z >= camera.near_plane;
        int b_inside = b.z >= camera.near_plane;

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