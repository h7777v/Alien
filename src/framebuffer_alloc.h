#pragma once

#include <stdlib.h>

#if defined(_MSC_VER)
    #include <malloc.h>
    #define fb_alloc(alignment, size) _aligned_malloc(size, alignment)
    #define fb_free(ptr) _aligned_free(ptr)
#else
    #define fb_alloc(alignment, size) aligned_alloc(alignment, size)
    #define fb_free(ptr) free(ptr)
#endif