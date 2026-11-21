#ifndef CPU_H
#define CPU_H

#include "export.h"

#include <stdint.h>

typedef struct {
    uint8_t vector;
    uint8_t avx;
    uint8_t avx2;
    uint8_t avx512f;
    uint8_t fma;
} cpu_features_t;

#ifdef __cplusplus
extern "C"
#endif

extern cpu_features_t cpu_features;

EXPORT void cpu_init();

#endif
