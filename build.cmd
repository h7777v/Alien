@echo off
setlocal

REM Very slow build for all arch, plz use cmake directly for testing

REM Windows x86
echo.
echo ===== Windows x86 =====
cmake -S . -B build/win-x86 -A Win32 -DRENDERER_PLATFORM=Windows -DRENDERER_ARCH=x86 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++
cmake --build build/win-x86 --config Release --parallel

REM Windows x64
echo.
echo ===== Windows x64 =====
cmake -S . -B build/win-x64 -A x64 -DRENDERER_PLATFORM=Windows -DRENDERER_ARCH=x86_64 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++
cmake --build build/win-x64 --config Release --parallel

REM Windows ARM
echo.
echo ===== Windows ARM =====
cmake -S . -B build/win-arm -A ARM -DRENDERER_PLATFORM=Windows -DRENDERER_ARCH=arm -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++
cmake --build build/win-arm --config Release --parallel

REM Windows ARM64
echo.
echo ===== Windows ARM64 =====
cmake -S . -B build/win-arm64 -A ARM64 -DRENDERER_PLATFORM=Windows -DRENDERER_ARCH=arm64 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++
cmake --build build/win-arm64 --config Release --parallel

REM Linux x86
echo.
echo ===== Linux x86 =====
cmake -S . -B build/linux-x86 -DCMAKE_BUILD_TYPE=Release -DRENDERER_PLATFORM=Linux -DRENDERER_ARCH=x86 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_C_FLAGS=-m32 -DCMAKE_CXX_FLAGS=-m32
cmake --build build/linux-x86 --parallel

REM Linux x64
echo.
echo ===== Linux x64 =====
cmake -S . -B build/linux-x64 -DCMAKE_BUILD_TYPE=Release -DRENDERER_PLATFORM=Linux -DRENDERER_ARCH=x86_64 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++
cmake --build build/linux-x64 --parallel

REM Linux ARM
echo.
echo ===== Linux ARM =====
cmake -S . -B build/linux-arm -DCMAKE_BUILD_TYPE=Release -DRENDERER_PLATFORM=Linux -DRENDERER_ARCH=arm -DCMAKE_SYSTEM_NAME=Linux -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_C_COMPILER_TARGET=arm-linux-gnueabihf -DCMAKE_CXX_COMPILER_TARGET=arm-linux-gnueabihf
cmake --build build/linux-arm --parallel

REM Linux ARM64
echo.
echo ===== Linux ARM64 =====
cmake -S . -B build/linux-arm64 -DCMAKE_BUILD_TYPE=Release -DRENDERER_PLATFORM=Linux -DRENDERER_ARCH=arm64 -DCMAKE_SYSTEM_NAME=Linux -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_C_COMPILER_TARGET=aarch64-linux-gnu -DCMAKE_CXX_COMPILER_TARGET=aarch64-linux-gnu
cmake --build build/linux-arm64 --parallel

echo.
echo ===== Build attempts finished =====
echo Check the output above for failed targets.
echo Apple arch are not build because I do not have the apple SDK
pause