load("@rules_cc//cc:defs.bzl", "cc_library")
load("@bazel_skylib//lib:selects.bzl", "selects")

package(default_visibility = ["//visibility:public"])

exports_files(
    [
        "ggml.h",
        "ggml.c",
        "whisper.h",
        "whisper.cpp",
    ] + glob(["examples/*.cpp"]) + glob(["examples/*.h"]),
)

HEADERS = [
    "ggml.h",
    "whisper.h",
]

EXAMPLE_HEADERS = [
    "examples/common-sdl.h",
    "examples/common.h",
    "examples/dr_wav.h",
]


genrule(
    name = "whispercpp",
    srcs = glob(["**/*"]),  # Include all necessary source files
    outs = ["whispercpp.so"],  # Output file
    cmd = "make -C $(location :.) $(MAKEFLAGS)",
    tools = ["Makefile"],
)

cc_library(
    name = "common",
    srcs = ["examples/common.cpp"],
    hdrs = EXAMPLE_HEADERS,
)

cc_library(
    name = "ggml",
    srcs = ["ggml.c"],
    hdrs = HEADERS,
)

cc_library(
    name = "whisper",
    srcs = ["whisper.cpp"],
    deps = [":ggml"],
)