project( distfs )
cmake_minimum_required( VERSION 3.10 )

set( CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=gnu++11" )

add_executable( ${PROJECT_NAME} main.cpp Multihash.cpp )