cmake_minimum_required(VERSION 3.8)
project(sally_msgs)

find_package(ament_cmake REQUIRED)
find_package(std_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)


rosidl_generate_interfaces(${PROJECT_NAME}
    "msg/ServoHead.msg"
    "msg/CarMovement.msg"
    DEPENDENCIES std_msgs
)


ament_export_dependencies(rosidl_default_runtime)

ament_package()