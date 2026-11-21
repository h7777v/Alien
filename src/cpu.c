#include "cpu.h"

#include <string.h>

#if defined(_M_X64) || defined(_M_IX86) || \
    defined(__x86_64__) || defined(__i386__)

    #define CPU_X86 1

    #if defined(_MSC_VER)
        #include <intrin.h>
    #else
        #include <cpuid.h>
    #endif

#else
    #define CPU_X86 0
#endif

cpu_features_t cpu_features = {0};

#if CPU_X86

static void cpu_cpuid(uint32_t leaf, uint32_t subleaf, uint32_t regs[4]){
#if defined(_MSC_VER)

    int r[4];
    __cpuidex(r, (int)leaf, (int)subleaf);

    regs[0] = (uint32_t)r[0];
    regs[1] = (uint32_t)r[1];
    regs[2] = (uint32_t)r[2];
    regs[3] = (uint32_t)r[3];

#else

    __cpuid_count(leaf, subleaf,
                  regs[0], regs[1],
                  regs[2], regs[3]);

#endif
}

static uint32_t cpu_max_leaf(void){
#if defined(_MSC_VER)

    int regs[4];
    __cpuid(regs, 0);
    return (uint32_t)regs[0];

#else

    return __get_cpuid_max(0, 0);

#endif
}

static uint64_t cpu_xgetbv(void){
#if defined(_MSC_VER)

    return _xgetbv(0);

#else

    uint32_t eax, edx;

    __asm__ volatile(
        "xgetbv"
        : "=a"(eax), "=d"(edx)
        : "c"(0)
    );

    return ((uint64_t)edx << 32) | eax;

#endif
}

static void cpu_detect_x86(void){
    uint32_t regs[4];

    if(cpu_max_leaf() < 1)
        return;

    cpu_cpuid(1, 0, regs);

    uint32_t ecx = regs[2];

    uint8_t osxsave = (ecx >> 27) & 1;
    uint8_t avx_hw  = (ecx >> 28) & 1;

    cpu_features.fma = (ecx >> 12) & 1;

    if(!osxsave || !avx_hw)
        return;

    uint64_t xcr0 = cpu_xgetbv();

    if((xcr0 & 0x6) != 0x6)
        return;

    cpu_features.avx = 1;

    if(cpu_max_leaf() < 7)
        return;

    cpu_cpuid(7, 0, regs);

    uint32_t ebx = regs[1];

    cpu_features.avx2 = (ebx >> 5) & 1;

    if((xcr0 & 0xE6) == 0xE6)
        cpu_features.avx512f = (ebx >> 16) & 1;

    cpu_features.vector =
        cpu_features.avx2 || cpu_features.avx512f;

    cpu_features.fma = cpu_features.fma;
}

#endif

void cpu_init(void){
    memset(&cpu_features, 0, sizeof(cpu_features));

#if CPU_X86

    cpu_detect_x86();

#elif defined(__aarch64__) || defined(_M_ARM64)

    //Do scalar for now

#elif defined(__arm__) || defined(_M_ARM)

    //Do scalar for now

#else

    //Do scalar

#endif
}
