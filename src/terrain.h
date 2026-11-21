#pragma once

#include "export.h"

#include <cstdint>

EXPORT void terrain_init(int seed, uint64_t craterDifficulty);
void generate_chunk(uint32_t cx, uint32_t cz, int detail, float* heightmap);
void triangulate_chunk(float* heightmap, int detail, triangle_light_t* chunk);