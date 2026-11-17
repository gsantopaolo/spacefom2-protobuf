cmake_minimum_required(VERSION 3.24)
project(spacefom_sample_cpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Protobuf C++ needs the runtime to match the generated code exactly
# (https://protobuf.dev/support/cross-version-runtime-guarantee/).
# Use an installed protobuf 36.2 if there is one; otherwise build it.
set(SPACEFOM_PROTOBUF_TAG v36.2)
find_package(protobuf CONFIG QUIET)
if(protobuf_FOUND AND NOT protobuf_VERSION VERSION_EQUAL 36.2)
  message(STATUS "Ignoring installed protobuf ${protobuf_VERSION}; need 36.2")
  set(protobuf_FOUND FALSE)
endif()
if(NOT protobuf_FOUND)
  message(STATUS "protobuf 36.2 not installed; building ${SPACEFOM_PROTOBUF_TAG} from source")
  include(FetchContent)
  set(protobuf_BUILD_TESTS OFF CACHE BOOL "" FORCE)
  set(protobuf_BUILD_PROTOC_BINARIES OFF CACHE BOOL "" FORCE)
  set(protobuf_INSTALL OFF CACHE BOOL "" FORCE)
  set(protobuf_ABSL_PROVIDER module CACHE STRING "" FORCE)
  set(ABSL_PROPAGATE_CXX_STD ON CACHE BOOL "" FORCE)
  FetchContent_Declare(
    protobuf
    GIT_REPOSITORY https://github.com/protocolbuffers/protobuf.git
    GIT_TAG ${SPACEFOM_PROTOBUF_TAG}
    GIT_SHALLOW TRUE
  )
  FetchContent_MakeAvailable(protobuf)
endif()

set(GENERATED ${CMAKE_CURRENT_SOURCE_DIR}/../generated/cpp)
file(GLOB GENERATED_SOURCES ${GENERATED}/siso/spacefom/v1/*.pb.cc)

add_library(spacefom_samples STATIC checks.cpp ${GENERATED_SOURCES})
target_include_directories(spacefom_samples PUBLIC ${GENERATED} ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(spacefom_samples PUBLIC protobuf::libprotobuf)
target_compile_definitions(spacefom_samples PUBLIC
  SPACEFOM_DATA_DIR="${CMAKE_CURRENT_SOURCE_DIR}/../data")

add_executable(reader reader.cpp)
target_link_libraries(reader PRIVATE spacefom_samples)

# Tests: GoogleTest v1.18.0, pinned to its release commit.
include(FetchContent)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/063de7e9578f82b369302001269680b4b1553359.tar.gz
)
set(INSTALL_GTEST OFF CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

enable_testing()
add_executable(samples_test samples_test.cpp)
target_link_libraries(samples_test PRIVATE spacefom_samples GTest::gtest_main)
include(GoogleTest)
gtest_discover_tests(samples_test)
add_test(NAME reader COMMAND reader)
