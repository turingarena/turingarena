import logging
import subprocess
from subprocess import CalledProcessError

from turingarena.sandbox.exceptions import CompilationFailed
from turingarena.sandbox.source import AlgorithmSource

logger = logging.getLogger(__name__)


class CppAlgorithmSource(AlgorithmSource):
    __slots__ = []

    def do_compile(self, algorithm_dir):
        cli = [
            "g++",
            "-std=c++14",
            "-Wno-unused-result",
            "-g", "-O2", "-static",
            "-o", "algorithm",
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
