cmake_minimum_required(VERSION 3.8)
project(lar_gazebo)

find_package(ament_cmake REQUIRED)

foreach(dir launch config maps models urdf worlds)
  if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/src/${dir}")
    install(
      DIRECTORY src/${dir}
      DESTINATION share/${PROJECT_NAME}
    )
  endif()
endforeach()

ament_package()
