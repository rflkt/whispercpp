cmake_minimum_required(VERSION 3.15)
project(WhisperCpp)

set(CMAKE_CXX_STANDARD 11)

# Define COPTS
#set(COPTS "-O3 -pthread -fPIC -Wall")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -pthread -fPIC -Wall")

if(UNIX AND NOT APPLE)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -pthread -fPIC -Wall")
#    list(APPEND COPTS "-mavx" "-mavx2" "-mfma" "-mf16c" "-msse3")
endif()

# Add includes and library directories

# Add source files
file(GLOB SRC_FILES src/whispercpp/*.cc)
file(GLOB HDR_FILES src/whispercpp/*.h)

# Define the libraries
#add_library(libwhisper STATIC IMPORTED)

### WHISPER CPP
include(ExternalProject)
ExternalProject_Add(
        git_whispercpp
        PREFIX ${CMAKE_CURRENT_BINARY_DIR}/libwhisper
        GIT_REPOSITORY git@github.com:ggerganov/whisper.cpp.git
        GIT_TAG v1.6.2
        GIT_SUBMODULES ""
        SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/extern/whispercpp
#        BUILD_COMMAND #${CMAKE_COMMAND} -E env
##        CC=${CMAKE_C_COMPILER} CXX=${CMAKE_CXX_COMPILER}
#        make -C <SOURCE_DIR> libwhisper.so
        BUILD_COMMAND make libwhisper.so
        BUILD_IN_SOURCE TRUE
        CONFIGURE_COMMAND ""
        UPDATE_COMMAND ""
#        INSTALL_COMMAND ""
        INSTALL_DIR ${CMAKE_BINARY_DIR}
        INSTALL_COMMAND cp <SOURCE_DIR>/libwhisper.so <INSTALL_DIR>/libwhisper.so
        BUILD_BYPRODUCTS <INSTALL_DIR>/libwhisper.so
)
ExternalProject_Get_Property(git_whispercpp SOURCE_DIR)
message(STATUS "SOURCE_DIR: ${SOURCE_DIR}")

SET(WHISPER_INCLUDE_DIRS ${SOURCE_DIR} ${SOURCE_DIR}/examples)
SET(WHISPER_LIB_DIR ${SOURCE_DIR})

add_library(whisper STATIC IMPORTED)
set_property(TARGET whisper PROPERTY IMPORTED_LOCATION ${CMAKE_BINARY_DIR}/libwhisper.so)

include_directories(${WHISPER_INCLUDE_DIRS})
add_dependencies(whisper git_whispercpp)

# WhisperCPP Commons
file(GLOB WHISPER_COMMON_SRC_FILES ${SOURCE_DIR}/examples/common*.cpp)
file(GLOB WHISPER_COMMON_HDR_FILES ${SOURCE_DIR}/examples/*.h ${SOURCE_DIR}/examples/*.hpp)
add_library(whisper_commons STATIC
        ${WHISPER_COMMON_SRC_FILES}
        ${WHISPER_COMMON_HDR_FILES}
)
target_compile_options(whisper_commons PRIVATE ${COPTS})
add_dependencies(whisper_commons git_whispercpp)


add_library(context STATIC
        ${SRC_FILES}
        ${HDR_FILES}
)
target_compile_options(context PRIVATE ${COPTS})
target_link_libraries(context whisper)

add_library(audio_lib STATIC
        src/whispercpp/audio.cc
        src/whispercpp/context.h
)
target_compile_options(audio_lib PRIVATE ${COPTS})

find_package(SDL2 REQUIRED)
include_directories(${SDL2_INCLUDE_DIRS})

target_link_libraries(audio_lib context SDL2::SDL2)

# Define the pybind11 extensions
find_package(Python COMPONENTS Development Interpreter REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})
find_package(pybind11 CONFIG REQUIRED)
include_directories(${pybind11_INCLUDE_DIRS})

pybind11_add_module(audio_cpp2py_export
        src/whispercpp/audio.cc
        src/whispercpp/audio.h
        src/whispercpp/context.cc
        src/whispercpp/context.h
        src/whispercpp/params.cc
)
target_compile_options(audio_cpp2py_export PRIVATE ${COPTS})
target_link_libraries(audio_cpp2py_export PRIVATE audio_lib)
target_link_libraries(audio_cpp2py_export PUBLIC pybind11::headers)
target_link_libraries(audio_cpp2py_export PUBLIC pybind11::module)

pybind11_add_module(api_cpp2py_export
        src/whispercpp/api_cpp2py_export.cc
        src/whispercpp/api_cpp2py_export.h
        src/whispercpp/context.cc
        src/whispercpp/context.h
        src/whispercpp/params.cc
)
target_compile_options(api_cpp2py_export PRIVATE ${COPTS})
target_link_libraries(api_cpp2py_export PRIVATE whisper)
target_link_libraries(api_cpp2py_export PRIVATE whisper_commons)

set_target_properties(api_cpp2py_export PROPERTIES BUILD_WITH_INSTALL_RPATH TRUE INSTALL_RPATH "${CMAKE_BINARY_DIR}")

# Copy shared objects
add_custom_command(TARGET audio_cpp2py_export POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:audio_cpp2py_export> ${CMAKE_CURRENT_SOURCE_DIR}/src/whispercpp/audio_cpp2py_export.so
        BYPRODUCTS ${CMAKE_CURRENT_SOURCE_DIR}/src/whispercpp/audio_cpp2py_export.so
)
add_custom_command(TARGET api_cpp2py_export POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:api_cpp2py_export> ${CMAKE_CURRENT_SOURCE_DIR}/src/whispercpp/api_cpp2py_export.so
        BYPRODUCTS ${CMAKE_CURRENT_SOURCE_DIR}/src/whispercpp/api_cpp2py_export.so
)


# Add Python package creation
set(PACKAGE_NAME "whispercpp")
set(PACKAGE_VERSION "0.0.17")
set(PACKAGE_AUTHOR "Aaron Pham")
set(PACKAGE_EMAIL "aarnphm@bentoml.com")
set(PACKAGE_DESCRIPTION "WhisperCPP Python bindings")
set(PACKAGE_URL "https://github.com/aarnphm/whispercpp")
set(PACKAGE_LICENSE "Apache-2.0")

#file(WRITE ${CMAKE_BINARY_DIR}/setup.py "
#from setuptools import setup, Extension
#setup(
#    name='${PACKAGE_NAME}',
#    version='${PACKAGE_VERSION}',
#    author='${PACKAGE_AUTHOR}',
#    author_email='${PACKAGE_EMAIL}',
#    description='${PACKAGE_DESCRIPTION}',
#    url='${PACKAGE_URL}',
#    license='${PACKAGE_LICENSE}',
#    packages=['src.whispercpp'],
#    ext_modules=[
#        Extension(
#            name='audio_cpp2py_export',
#            sources=['src/whispercpp/audio_cpp2py_export.so'],
#        ),
#        Extension(
#            name='api_cpp2py_export',
#            sources=['src/whispercpp/api_cpp2py_export.so'],
#        ),
#    ],
#    classifiers=[
#        'Development Status :: 5 - Production/Stable',
#        'Intended Audience :: Developers',
#        'License :: OSI Approved :: Apache Software License',
#        'Operating System :: POSIX :: Linux',
#        'Topic :: Scientific/Engineering',
#        'Topic :: Software Development',
#        'Programming Language :: Python',
#        'Programming Language :: C++',
#        'Programming Language :: Python :: 3 :: Only',
#        'Programming Language :: Python :: 3.8',
#        'Programming Language :: Python :: 3.9',
#        'Programming Language :: Python :: 3.10',
#        'Programming Language :: Python :: 3.11',
#    ],
#)
#")

# Add a target to create the wheel
add_custom_target(whispercpp_wheel ALL
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/README.rst ${CMAKE_BINARY_DIR}
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/LICENSE ${CMAKE_BINARY_DIR}
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/pyproject.toml ${CMAKE_BINARY_DIR}
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/src ${CMAKE_BINARY_DIR}/src
        COMMAND ${CMAKE_COMMAND} -E tar cvzf whispercpp-${PACKAGE_VERSION}-py3-none-any.whl ${CMAKE_BINARY_DIR}
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        BYPRODUCTS whispercpp-${PACKAGE_VERSION}-py3-none-any.whl
)

