import logging
import os
import resource
import subprocess
from contextlib import contextmanager
from tempfile import TemporaryDirectory

import pkg_resources

from turingarena.protocol.module import locate_interface_dir
from turingarena.sandbox.exceptions import CompilationFailed, AlgorithmRuntimeError
from turingarena.sandbox.executable import AlgorithmExecutable
from turingarena.sandbox.source import AlgorithmSource

logger = logging.getLogger(__name__)


class CppAlgorithmSource(AlgorithmSource):
    __slots__ = []

    def do_compile(self, algorithm_dir):
        protocol_dir = locate_interface_dir(self.interface)

        skeleton_path = os.path.join(
            protocol_dir,
            f"_skeletons/cpp/skeleton.cpp",
        )

        sandbox_path = pkg_resources.resource_filename(__name__, "sandbox.c")
        source_filename = os.path.join(algorithm_dir, "source.cpp")
        with open(source_filename, "w") as f:
            f.write(self.text)

        cli = [
            "g++",
            "-g", "-O2", "-static",
            "-o", "algorithm",
            sandbox_path,
            skeleton_path,
            "source.cpp",
        ]
        logger.debug(f"Running {' '.join(cli)}")

        compilation_output_filename = os.path.join(algorithm_dir, "compilation_output.txt")
        with open(compilation_output_filename, "w") as compilation_output:
            compiler = subprocess.run(
                cli,
                cwd=algorithm_dir,
                stderr=compilation_output,
                universal_newlines=True,
            )
        with open(compilation_output_filename) as compilation_output:
            for line in compilation_output:
                logger.debug(f"g++: {line.rstrip()}")

        if compiler.returncode == 0:
            logger.info("Compilation successful")
        elif compiler.returncode == 1:
            raise CompilationFailed
        else:
            raise ValueError("Unable to invoke g++ properly")


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
