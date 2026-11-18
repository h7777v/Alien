#pragma once

#ifdef __cplusplus
#ifdef _WIN32
    #define EXPORT extern "C" __declspec(dllexport)
#elif defined(__linux__)
    #define EXPORT extern "C" __attribute__((visibility("default")))
#elif defined(__APPLE__)
    #define EXPORT extern "C" __attribute__((visibility("default")))
#endif
#else
#ifdef _WIN32
    #define EXPORT __declspec(dllexport)
#elif defined(__linux__)
    #define EXPORT __attribute__((visibility("default")))
#elif defined(__APPLE__)
    #define EXPORT __attribute__((visibility("default")))
#endif
#endif