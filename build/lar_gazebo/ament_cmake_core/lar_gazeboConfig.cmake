# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_lar_gazebo_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED lar_gazebo_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(lar_gazebo_FOUND FALSE)
  elseif(NOT lar_gazebo_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(lar_gazebo_FOUND FALSE)
  endif()
  return()
endif()
set(_lar_gazebo_CONFIG_INCLUDED TRUE)

# output package information
if(NOT lar_gazebo_FIND_QUIETLY)
  message(STATUS "Found lar_gazebo: 2.0.0 (${lar_gazebo_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'lar_gazebo' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT lar_gazebo_DEPRECATED_QUIET)
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(lar_gazebo_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${lar_gazebo_DIR}/${_extra}")
endforeach()
