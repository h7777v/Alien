#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "export.h"

typedef struct {
    uint32_t* buffer;
    int width;
    int height;
} Framebuffer;

extern Framebuffer framebuffer;

EXPORT bool framebuffer_init(int width, int height);
EXPORT void framebuffer_destroy();

void framebuffer_clear(uint32_t color);
void framebuffer_set_pixel(int x, int y, uint32_t color);

uint32_t framebuffer_get_pixel(int x, int y);
uint32_t* framebuffer_get_pixels();