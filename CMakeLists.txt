cmake_minimum_required(VERSION 3.20)

project(C_AI_Movie_Shorts LANGUAGES C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include(FetchContent)

# ---------------- options: which apps to build ----------------
option(BUILD_CLI_APP     "Build CLI app (src/cli.c)" ON)
option(BUILD_RAYLIB_UI   "Build Raylib UI (src/main.c)" ON)
option(BUILD_IUP_UI      "Build IUP UI (src/ui_main.c)" OFF)

# ---------------- raylib ----------------
set(BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)

FetchContent_Declare(
  raylib
  GIT_REPOSITORY https://github.com/raysan5/raylib.git
  GIT_TAG 5.5
)
FetchContent_MakeAvailable(raylib)

# ---------------- cJSON ----------------
# avoid "uninstall" target collision
set(ENABLE_CJSON_UNINSTALL OFF CACHE BOOL "" FORCE)
set(ENABLE_CJSON_TEST OFF CACHE BOOL "" FORCE)

FetchContent_Declare(
  cjson
  GIT_REPOSITORY https://github.com/DaveGamble/cJSON.git
  GIT_TAG v1.7.16
)
FetchContent_MakeAvailable(cjson)

# ---------------- system deps ----------------
find_package(CURL REQUIRED)
find_package(Threads REQUIRED)

# ---------------- shared core library (NO main() here) ----------------
add_library(movie_core
  src/generator.c
  src/platform_open.c
)

target_include_directories(movie_core PUBLIC
  "${CMAKE_CURRENT_SOURCE_DIR}/src"
  "${CMAKE_CURRENT_SOURCE_DIR}"
)

# Ensure generator.c can find cJSON.h
if(DEFINED cjson_SOURCE_DIR)
  target_include_directories(movie_core PUBLIC "${cjson_SOURCE_DIR}")
elseif(DEFINED cJSON_SOURCE_DIR)
  target_include_directories(movie_core PUBLIC "${cJSON_SOURCE_DIR}")
endif()

target_link_libraries(movie_core PUBLIC
  CURL::libcurl
  Threads::Threads
)

if (TARGET cjson)
  target_link_libraries(movie_core PUBLIC cjson)
else()
  message(FATAL_ERROR "cJSON target not found (expected target named 'cjson').")
endif()

# Warnings
if(MSVC)
  target_compile_definitions(movie_core PRIVATE _CRT_SECURE_NO_WARNINGS)
else()
  target_compile_options(movie_core PRIVATE
    -Wall -Wextra -Wno-unused-parameter -Wno-unused-const-variable
  )
endif()

# ---------------- CLI executable ----------------
if(BUILD_CLI_APP)
  add_executable(movie_summary_cli src/cli.c)
  target_link_libraries(movie_summary_cli PRIVATE movie_core)
endif()

# ---------------- Raylib UI executable ----------------
if(BUILD_RAYLIB_UI)
  add_executable(movie_summary_bot src/main.c)
  target_link_libraries(movie_summary_bot PRIVATE movie_core raylib)

  # macOS frameworks (safe/robust)
  if(APPLE)
    target_link_libraries(movie_summary_bot PRIVATE
      "-framework Cocoa"
      "-framework IOKit"
      "-framework OpenGL"
      "-framework CoreVideo"
      "-framework CoreAudio"
      "-framework AudioToolbox"
    )
  endif()
endif()

# ---------------- IUP UI executable (optional) ----------------
# Only enable if you actually have IUP integrated in src/ui_main.c
if(BUILD_IUP_UI)
  add_executable(movie_summary_iup src/ui_main.c)
  target_link_libraries(movie_summary_iup PRIVATE movie_core)
endif()
