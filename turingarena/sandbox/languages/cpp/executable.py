import logging
import os
import subprocess
from contextlib import contextmanager
from tempfile import TemporaryDirectory

from turingarena.sandbox.executable import AlgorithmExecutable
from turingarena.sandbox.rlimits import set_memory_and_time_limits

logger = logging.getLogger(__name__)


class ElfAlgorithmExecutable(AlgorithmExecutable):
    __slots__ = []

    @contextmanager
    def run(self, connection):
        executable_filename = os.path.join(self.algorithm_dir, "algorithm")
        with TemporaryDirectory(dir="/tmp", prefix="elf_cwd_") as cwd:
            with self.manage_process(
                    subprocess.Popen(
                        [executable_filename],
                        universal_newlines=True,
                        preexec_fn=lambda: set_memory_and_time_limits(),
                        cwd=cwd,
                        stdin=connection.downward,
                        stdout=connection.upward,
                        bufsize=1,
                    ),
                    get_stack_trace=lambda: self.get_back_trace(executable_filename, cwd)
            ) as process:
                yield process

    @staticmethod
    def get_back_trace(executable_filename, cwd):
        gdb_run = subprocess.run(
            [
                "gdb",
                "-se", executable_filename,
                "-c", os.path.join(cwd, "core"),
                "-q",
                "-batch",
                "-ex", "backtrace",
            ],
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        return gdb_run.stdout
