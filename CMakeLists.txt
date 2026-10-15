cmake_minimum_required(VERSION 3.20)
project(overhang_bench LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "" FORCE)
endif()

option(OB_BUILD_VIEWER "Build the Polyscope viewer" ON)

include(FetchContent)

# libigl (header-only mode); it brings Eigen with it.
set(LIBIGL_USE_STATIC_LIBRARY OFF CACHE BOOL "" FORCE)
FetchContent_Declare(libigl
  GIT_REPOSITORY https://github.com/libigl/libigl.git
  GIT_TAG v2.5.0
  GIT_SHALLOW TRUE)
FetchContent_MakeAvailable(libigl)

# LBFGSpp (header-only L-BFGS-B)
FetchContent_Declare(lbfgspp
  GIT_REPOSITORY https://github.com/yixuan/LBFGSpp.git
  GIT_TAG v0.4.0
  GIT_SHALLOW TRUE)
FetchContent_GetProperties(lbfgspp)
if(NOT lbfgspp_POPULATED)
  FetchContent_Populate(lbfgspp)
endif()

find_package(OpenMP)

add_library(ob_core INTERFACE)
target_include_directories(ob_core INTERFACE
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${lbfgspp_SOURCE_DIR}/include)
target_link_libraries(ob_core INTERFACE igl::core)
if(OpenMP_CXX_FOUND)
  target_link_libraries(ob_core INTERFACE OpenMP::OpenMP_CXX)
endif()
if(MSVC)
  target_compile_definitions(ob_core INTERFACE _USE_MATH_DEFINES NOMINMAX)
  target_compile_options(ob_core INTERFACE /bigobj)
endif()

add_executable(bench src/bench.cpp)
target_link_libraries(bench PRIVATE ob_core)

if(OB_BUILD_VIEWER)
  FetchContent_Declare(polyscope
    GIT_REPOSITORY https://github.com/nmwsharp/polyscope.git
    GIT_TAG v2.3.0
    GIT_SHALLOW TRUE)
  FetchContent_MakeAvailable(polyscope)
  add_executable(viewer src/viewer.cpp)
  target_link_libraries(viewer PRIVATE ob_core polyscope)
endif()
