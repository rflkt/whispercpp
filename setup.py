import os
from os import path
from pathlib import Path
from subprocess import check_output, CalledProcessError

from setuptools import setup, Command, Extension
from setuptools.dist import Distribution
from setuptools.errors import CompileError

WITH_CUDA = os.getenv("WHISPER_CUDA", "0") in ("1", "true", "True", "yes")


def update_submodules(directory: str):
    check_output(["git", "init"])
    check_output(["git", "submodule", "sync", "--recursive"], cwd=directory)
    check_output(["git", "submodule", "update", "--init", "--recursive"], cwd=directory)


class BuildExtension(Command):
    def run(self):
        wd = path.dirname(path.abspath(__file__))
        if not path.exists(path.join(wd, "src", "whispercpp", "api_cpp2py_export.so")):
            update_submodules(wd)
            print("Building pybind11 extension...")
            bazel_script = Path(wd) / "tools" / "bazel"
            bazel_command = [bazel_script.__fspath__(), "run", "//:extensions"]
            if self.with_cuda:
                bazel_command.append("--define=WHISPER_CUDA=1")
            try:
                check_output(bazel_command, cwd=wd)
            except CalledProcessError as e:
                print(e.output)
                raise CompileError from e

    def initialize_options(self):
        self.with_cuda = None

    def finalize_options(self):
        if self.with_cuda is None:
            self.with_cuda = WITH_CUDA
        self.with_cuda = self.with_cuda in ("1", "true", "True", "yes", True)


class WhisperDistribution(Distribution):
    def has_ext_modules(self):
        return True


setup(
    distclass=WhisperDistribution,
    ext_modules=[
        Extension(
            "whispercpp",
            sources=["src/whispercpp/api_cpp2py_export.so"],
            include_dirs=[
                "./extern/whispercpp",
                "./extern/pybind11/include",
                "./src/whispercpp/",
            ],
        )
    ],
    cmdclass={"build_ext": BuildExtension},
)
