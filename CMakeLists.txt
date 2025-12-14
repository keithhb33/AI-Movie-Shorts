cmake_minimum_required(VERSION 3.16)
project(ai_movie_shorts_c C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(PkgConfig REQUIRED)
find_package(CURL REQUIRED)

pkg_check_modules(CJSON REQUIRED IMPORTED_TARGET libcjson)

add_executable(movie_summary_bot main.c)

target_link_libraries(movie_summary_bot PRIVATE
  CURL::libcurl
  PkgConfig::CJSON
)
