#include <stdbool.h>
#include <stdint.h>
#include <immintrin.h>

#include "cpu.h"

#include "framebuffer_alloc.h"
#include "framebuffer.h"

Framebuffer framebuffer = {
    .buffer = NULL, 
    .width = 0, 
    .height = 0, 
};

bool framebuffer_init(int width, int height){
    size_t size = (size_t)width * height * sizeof(uint32_t);

    size = (size + 63) & ~(size_t)63;

    void* tmp_buffer_ptr = fb_alloc(64, size);
    if (tmp_buffer_ptr == NULL)return false;

    framebuffer.buffer = tmp_buffer_ptr;
    framebuffer.width = width;
    framebuffer.height = height;

    return true;
}

void framebuffer_destroy(){
    fb_free(framebuffer.buffer);
    framebuffer.buffer = NULL;
    framebuffer.width = 0;
    framebuffer.height = 0;
}

void framebuffer_clear(uint32_t color){
    if(cpu_features.avx2){
        __m256i value = _mm256_set1_epi32(color);
        for(size_t i = 0; i < framebuffer.width * framebuffer.height; i += 8){
            _mm256_store_si256(&framebuffer.buffer[i], value);
        }
    }else{
        //non simd approach
        int cache;
        for(int i = 0; i < framebuffer.height; i++){
            cache = i * framebuffer.width;
            for(int j = 0; j < framebuffer.width; j++){
                framebuffer.buffer[j + cache] = color;
            }
        }
    }
}

void framebuffer_set_pixel(int x, int y, uint32_t color){
    framebuffer.buffer[x + framebuffer.width * y] = color;
}

uint32_t framebuffer_get_pixel(int x, int y){
    return framebuffer.buffer[x + framebuffer.width * y];
}

uint32_t* framebuffer_get_pixels(){
    return framebuffer.buffer;
}