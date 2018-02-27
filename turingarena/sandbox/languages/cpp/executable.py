import logging
import os
import resource
import subprocess
from contextlib import contextmanager
from tempfile import TemporaryDirectory

from turingarena.sandbox.exceptions import AlgorithmRuntimeError
from turingarena.sandbox.executable import AlgorithmExecutable

logger = logging.getLogger(__name__)


class ElfAlgorithmExecutable(AlgorithmExecutable):
    __slots__ = []

    @contextmanager
    def run(self, connection):
        executable_filename = os.path.join(self.algorithm_dir, "algorithm")
        with TemporaryDirectory(dir="/dev/shm", prefix="elf_cwd_") as cwd:
            with subprocess.Popen(
                    [executable_filename],
                    universal_newlines=True,
                    preexec_fn=preexec_fn,
                    cwd=cwd,
                    stdin=connection.downward,
                    stdout=connection.upward,
                    bufsize=1,
            ) as p:
                logger.debug(f"starting process")
                yield p
                logger.debug(f"waiting for process")

            if p.returncode != 0:
                bt = self.get_back_trace(executable_filename, cwd)
                logger.warning(f"process terminated with returncode {p.returncode}")
                raise AlgorithmRuntimeError(
                    f"invalid return code {p.returncode}",
                    bt,
                )

    def get_back_trace(self, executable_filename, cwd):
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


def preexec_fn():
    memory_limit = 16 * 1024 * 1024
    time_limit = 1
    core_limit = 32 * 1024 * 1024

    resource.setrlimit(
        resource.RLIMIT_CORE,
        (core_limit, resource.RLIM_INFINITY),
    )
    resource.setrlimit(
        resource.RLIMIT_STACK,
        (resource.RLIM_INFINITY, resource.RLIM_INFINITY),
    )
    resource.setrlimit(
        resource.RLIMIT_CPU,
        (time_limit, resource.RLIM_INFINITY),
        # use soft < hard to ensure SIGXCPU is raised instead of SIGKILL
        # see setrlimit(2)
    )
    resource.setrlimit(
        resource.RLIMIT_AS,
        (memory_limit, resource.RLIM_INFINITY),
    )
