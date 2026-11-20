#pragma once

#include <stdbool.h>
#include "export.h"

typedef struct {
    float* buffer;
    int width;
    int height;
} Zbuffer;

extern Zbuffer zbuffer;

EXPORT bool Zbuffer_init(int width, int height);
EXPORT void Zbuffer_destroy();

void Zbuffer_clear();
void Zbuffer_set_pixel(int x, int y, float index);

float Zbuffer_get_pixel(int x, int y);
float* Zbuffer_get_pixels();