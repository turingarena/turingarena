import logging
import os
import subprocess
from contextlib import contextmanager
from subprocess import CalledProcessError
from tempfile import TemporaryDirectory

import pkg_resources

from turingarena.sandbox.exceptions import CompilationFailed
from turingarena.sandbox.process import PopenProcess
from turingarena.sandbox.rlimits import set_memory_and_time_limits
from turingarena.sandbox.source import AlgorithmSource

logger = logging.getLogger(__name__)


class CppAlgorithmSource(AlgorithmSource):
    __slots__ = []

    @contextmanager
    def run(self, connection):
        sandbox_path = pkg_resources.resource_filename(__name__, "sandbox.py")

        with TemporaryDirectory(dir="/tmp", prefix="elf_cwd_") as cwd:
            with open(os.path.join(cwd, f"skeleton.cpp"), "w") as f:
                self.language.skeleton_generator(self.interface).write_to_file(f)

            cli = [
                "g++",
                "-std=c++14",
                "-Wno-unused-result",
                "-g", "-O2", "-static",
                "-o", "algorithm",
                "skeleton.cpp",
                self.source_path,
            ]
            logger.debug(f"Running {' '.join(cli)}")
            try:
                subprocess.run(
                    cli,
                    cwd=cwd,
                    universal_newlines=True,
                    check=True,
                )
            except CalledProcessError as e:
                if e.returncode == 1:
                    raise CompilationFailed
                raise

            with PopenProcess.run(
                    ["python3", sandbox_path, "algorithm"],
                    universal_newlines=True,
                    preexec_fn=lambda: set_memory_and_time_limits(),
                    cwd=cwd,
                    stdin=connection.downward,
                    stdout=connection.upward,
                    bufsize=1,
            ) as process:
                yield process
