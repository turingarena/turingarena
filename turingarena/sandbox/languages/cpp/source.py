import logging
import os
import subprocess
from subprocess import CalledProcessError

import pkg_resources

from turingarena.common import write_to_file
from turingarena.interface.skeleton.cpp import CppSkeletonCodeGen
from turingarena.sandbox.exceptions import CompilationFailed
from turingarena.sandbox.source import AlgorithmSource

logger = logging.getLogger(__name__)


class CppAlgorithmSource(AlgorithmSource):
    __slots__ = []

    def do_compile(self, algorithm_dir):
        sandbox_path = pkg_resources.resource_filename(__name__, "sandbox.c")

        skeleton_filename = os.path.join(algorithm_dir, "skeleton.cpp")
        with open(skeleton_filename, "w") as f:
            write_to_file(CppSkeletonCodeGen(self.interface).generate(), f)

        source_filename = os.path.join(algorithm_dir, "source.cpp")
        with open(source_filename, "w") as f:
            f.write(self.text)

        cli = [
            "g++",
            "-std=c++14",
            "-Wno-unused-result",
            "-g", "-O2", "-static",
            "-o", "algorithm",
            sandbox_path,
            "skeleton.cpp",
            "source.cpp",
        ]
        logger.debug(f"Running {' '.join(cli)}")

        try:
            subprocess.run(
                cli,
                cwd=algorithm_dir,
                universal_newlines=True,
                check=True,
            )
        except CalledProcessError as e:
            if e.returncode == 1:
                raise CompilationFailed
            raise
