project(example)
cmake_minimum_required(VERSION 2.8)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -O2 -march=native -pthread")

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/modules/")

set(SRC
  ./example.cpp
  )

find_package(GUROBI REQUIRED)
include_directories(${GUROBI_INCLUDE_DIR})

add_executable(${PROJECT_NAME} ${SRC})
target_link_libraries(${PROJECT_NAME}
  ${GUROBI_LIBRARIES}
  )
