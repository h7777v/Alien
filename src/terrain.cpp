#include <algorithm>
#include <cmath>
#include <cstdint>

#include "triangles.h"
#include "terrain.h"

#include "lighting.h"
#include "sun.h"

#include "FastNoiseLite.h"

FastNoiseLite noise;
uint64_t craterDifficulty_;
int seed_;

void terrain_init(int seed, uint64_t craterDifficulty){
    craterDifficulty_ = craterDifficulty;
    seed_ = seed; 

    noise.SetSeed(seed);
    noise.SetNoiseType(FastNoiseLite::NoiseType_Perlin);

    noise.SetFrequency(0.002f);

    noise.SetFractalType(FastNoiseLite::FractalType_FBm);
    noise.SetFractalOctaves(5);
    noise.SetFractalLacunarity(2.0f);
    noise.SetFractalGain(0.5f);
}

static inline float terrain_height(float x, float z){
    float large = noise.GetNoise(x * 0.25f, z * 0.25f);
    float medium = noise.GetNoise(x, z);
    float detail = noise.GetNoise(x * 4.0f, z * 4.0f);

    return large * 20.0f + medium * 5.0f + detail * 0.8f;
}

//Hash function

static inline uint64_t mix64(uint64_t x){
    x += 0x9e3779b97f4a7c15ULL;
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
    x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
    return x ^ (x >> 31);
}

static inline uint64_t hash2(int x, int z, uint64_t seed){
    return mix64(mix64(seed ^ (uint32_t)x) ^ (uint32_t)z);
}

static inline float normalise(uint64_t h){
    return static_cast<float>(h >> 40) * 5.9604645e-8f;
}

//Craters and stuff

static inline float SmoothMin(float a, float b, float k){
    float h = std::max(k - std::abs(a - b), 0.0f) / k;
    return std::min(a, b) - h * h * k * 0.25f;
}

static inline float CavityShape(float x, float depth){
    return x * x - depth;
}

static inline float RimShape(float x, float rimWidth, float rimSteepness){
    if(x >= 1.0f + rimWidth)return 0.0f;

    x = std::abs(x) - 1 - rimWidth;
    return rimSteepness * x * x;
}

static inline float CraterShape(float x, float rimWidth, float rimSteepness, float floorHeight, float depth, float smoothness){
    float cavity = CavityShape(x, depth);
    float rim = RimShape(x, rimWidth, rimSteepness);

    float shape = SmoothMin(cavity, rim, smoothness);

    return -SmoothMin(-shape, -floorHeight, smoothness);
}

void generate_chunk(uint32_t cx, uint32_t cz, int detail, float* heightmap){
    if(detail == 0){
        for(uint64_t x = 2048 * cx; x < 2048 * cx + 2048; x++){
            for(uint64_t z = 2048 * cz; z < 2048 * cz + 2048; z++){
                heightmap[z*2048 + x] = terrain_height(static_cast<float>(x) * 0.5, static_cast<float>(z) * 0.5);
            }
        }
    }else if(detail == 1){
        for(uint64_t x = 1024 * cx; x < 1024 * cx + 1024; x++){
            for(uint64_t z = 1024 * cz; z < 1024 * cz + 1024; z++){
                heightmap[z*1024 + x] = terrain_height(static_cast<float>(x), static_cast<float>(z));
            }
        }
    }else if(detail == 2){
        for(uint64_t x = 512 * cx; x < 512 * cx + 512; x++){
            for(uint64_t z = 512 * cz; z < 512 * cz + 512; z++){
                heightmap[z*512 + x] = terrain_height(static_cast<float>(x << 1), static_cast<float>(z << 1));
            }
        }
    }

    int64_t border = 288;
    uint32_t resolution = 2048 >> detail;

    /*for(int64_t x = 2048LL * cx - border; x < 2048LL * cx + 2048 + border; x++){
        for(int64_t z = 2048LL * cz - border; z < 2048LL * cz + 2048 + border; z++){
            float wx = static_cast<float>(x) * 0.5f;
            float wz = static_cast<float>(z) * 0.5f;
            if(hash2(wx, wz, seed_) < craterDifficulty_){
                float radius = 6.0f + 90.0f * normalise(hash2(wx, wz, seed_ + 1));
                float depth = radius * (0.10f + 0.15f * normalise(hash2(wx, wz, seed_ + 2)));
                float rim_width = 0.10f + 0.40f * normalise(hash2(wx, wz, seed_ + 3));
                float rim_steepness = 1.0f + 3.0f * normalise(hash2(wx, wz, seed_ + 4));
                float floor_height = 0.1f + 0.4f * normalise(hash2(wx, wz, seed_ + 5));
                float smoothness = 0.2f + 0.8f * normalise(hash2(wx, wz, seed_ + 6));

                int64_t reach = static_cast<int64_t>(std::ceil(radius * (1.0f + rim_width) * 2.0f));

                for(int64_t i = std::max<int64_t>(2048 * cx, x - reach); i <= std::min<int64_t>(2048 * cx + 2047, x + reach); i++){
                    for(int64_t j = std::max<int64_t>(2048 * cz, z - reach); j <= std::min<int64_t>(2048 * cz + 2047, z + reach); j++){
                        float dx = static_cast<float>(i - x) * 0.5f;
                        float dz = static_cast<float>(j - z) * 0.5f;
                        float r = std::sqrt(dx * dx + dz * dz) / radius;

                        if(r < 1.0f + rim_width){
                            heightmap[(j - resolution * cz) * resolution + (i - resolution * cx)] += CraterShape(
                                r,
                                rim_width,
                                rim_steepness,
                                floor_height,
                                depth,
                                smoothness
                            );
                        }
                    }
                }
            }
        }
    }*/
}

void triangulate_chunk(float* heightmap, int detail, triangle_light_t* chunk){
    uint32_t resolution = 2048 >> detail;
    float spacing = 0.5f * (1 << detail);
    uint64_t index = 0;

    for(uint32_t z = 0; z < resolution - 1; z++){
        for(uint32_t x = 0; x < resolution - 1; x++){
            uint32_t a = z * resolution + x;
            uint32_t b = a + 1;
            uint32_t c = a + resolution;
            uint32_t d = c + 1;

            vertex_t va = {x * spacing, heightmap[a], z * spacing};
            vertex_t vb = {(x + 1) * spacing, heightmap[b], z * spacing};
            vertex_t vc = {x * spacing, heightmap[c], (z + 1) * spacing};
            vertex_t vd = {(x + 1) * spacing, heightmap[d], (z + 1) * spacing};

            vertex_t normal1 = calculate_normal(va, vc, vb);
            vertex_t normal2 = calculate_normal(vb, vc, vd);

            uint8_t brightness1 = calculate_brightness(normal1, sun_direction);
            uint8_t brightness2 = calculate_brightness(normal2, sun_direction);

            chunk[index++] = {
                {va, vc, vb},
                brightness1
            };

            chunk[index++] = {
                {vb, vc, vd},
                brightness2
            };
        }
    }
}