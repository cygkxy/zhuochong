cmake_minimum_required(VERSION 3.10)
project(RainbowPet VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Windows GDI+ 链接
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -mwindows -DUNICODE -D_UNICODE -static-libgcc -static-libstdc++")

file(GLOB_RECURSE SOURCES src/*.cpp)

add_executable(RainbowPet ${SOURCES})

target_include_directories(RainbowPet PRIVATE src external)
target_link_libraries(RainbowPet PRIVATE gdi32 gdiplus winhttp ole32)
