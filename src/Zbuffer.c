#include <stdbool.h>
#include <math.h>
#include <immintrin.h>

#include "cpu.h"

#include "framebuffer_alloc.h"
#include "Zbuffer.h"

Zbuffer zbuffer = {
    .buffer = NULL, 
    .width = 0, 
    .height = 0, 
};

bool Zbuffer_init(int width, int height){
    size_t size = (size_t)width * height * sizeof(float);

    size = (size + 63) & ~(size_t)63;

    void* tmp_buffer_ptr = fb_alloc(64, size);
    if (tmp_buffer_ptr == NULL)return false;

    zbuffer.buffer = tmp_buffer_ptr;
    zbuffer.width = width;
    zbuffer.height = height;

    return true;
}

void Zbuffer_destroy(){
    fb_free(zbuffer.buffer);
    zbuffer.buffer = NULL;
    zbuffer.width = 0;
    zbuffer.height = 0;
}

void Zbuffer_clear(){
    if(cpu_features.avx2){
        __m256 value = _mm256_set1_ps(INFINITY);
        for(size_t i = 0; i < zbuffer.width * zbuffer.height; i += 8){
            _mm256_store_ps(&zbuffer.buffer[i], value);
        }
    }else{
        //non simd approach
        int cache;
        for(int i = 0; i < zbuffer.height; i++){
            cache = i * zbuffer.width;
            for(int j = 0; j < zbuffer.width; j++){
                zbuffer.buffer[j + cache] = INFINITY;
            }
        }
    }
}

void Zbuffer_set_pixel(int x, int y, float index){
    zbuffer.buffer[x + zbuffer.width * y] = index;
}

float Zbuffer_get_pixel(int x, int y){
    return zbuffer.buffer[x + zbuffer.width * y];
}

float* Zbuffer_get_pixels(){
    return zbuffer.buffer;
}