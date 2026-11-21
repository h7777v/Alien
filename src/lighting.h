#pragma once

#include <cmath>

#include "triangles.h"

static inline vertex_t cross(vertex_t a, vertex_t b){
    return {
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

static inline float dot(vertex_t a, vertex_t b){
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline vertex_t normalize(vertex_t v){
    float length = sqrtf(dot(v, v));

    return {
        v.x / length,
        v.y / length,
        v.z / length
    };
}

static inline vertex_t calculate_normal(vertex_t a, vertex_t b, vertex_t c){
    vertex_t ab = {
        b.x - a.x,
        b.y - a.y,
        b.z - a.z
    };

    vertex_t ac = {
        c.x - a.x,
        c.y - a.y,
        c.z - a.z
    };

    vertex_t normal = {
        ab.y * ac.z - ab.z * ac.y,
        ab.z * ac.x - ab.x * ac.z,
        ab.x * ac.y - ab.y * ac.x
    };

    float length = sqrtf(
        normal.x * normal.x +
        normal.y * normal.y +
        normal.z * normal.z
    );

    return {
        normal.x / length,
        normal.y / length,
        normal.z / length
    };
}

static inline uint8_t calculate_brightness(vertex_t normal, vertex_t light_direction){
    float brightness = normal.x * light_direction.x
                     + normal.y * light_direction.y
                     + normal.z * light_direction.z;

    if(brightness < 0.0f)brightness = 0.0f;

    if(brightness > 1.0f)brightness = 1.0f;

    return static_cast<uint8_t>(brightness * 255.0f);
}

static inline uint32_t apply_brightness(uint32_t color, uint8_t brightness){
    uint32_t r = ((color >> 16) & 0xFF) * brightness * (1.0f / 255.0f);
    uint32_t g = ((color >> 8)  & 0xFF) * brightness * (1.0f / 255.0f);
    uint32_t b = (color & 0xFF) * brightness * (1.0f / 255.0f);

    return (color & 0xFF000000) | (r << 16) | (g << 8) | b;
}