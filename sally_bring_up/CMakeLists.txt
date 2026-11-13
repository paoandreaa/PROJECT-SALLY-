cmake_minimum_required(VERSION 3.8)

project(sally_bring_up
    VERSION 1.0.0
    DESCRIPTION "Sally bring up package for unify / launch all project with one file ( launch )"
    LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    add_compile_options(
        -Wall
        -Wextra
        -Wpedantic
        -Werror=return-type
    )
endif()

find_package(ament_cmake REQUIRED)

install(DIRECTORY config launch
    DESTINATION share/${PROJECT_NAME}
)

ament_package()