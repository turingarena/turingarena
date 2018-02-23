import logging
import os
import subprocess
from contextlib import contextmanager

import pkg_resources

from turingarena.protocol.module import locate_protocol_dir
from turingarena.sandbox.exceptions import CompilationFailed, AlgorithmRuntimeError
from turingarena.sandbox.executable import AlgorithmExecutable
from turingarena.sandbox.source import AlgorithmSource

logger = logging.getLogger(__name__)


class CppAlgorithmSource(AlgorithmSource):
    __slots__ = []

    def do_compile(self, algorithm_dir):
        protocol, interface_name = self.interface.split(":")
        protocol_dir = locate_protocol_dir(protocol)

        skeleton_path = os.path.join(
            protocol_dir,
            f"_skeletons/{interface_name}/cpp/skeleton.cpp",
        )

        sandbox_path = pkg_resources.resource_filename(__name__, "sandbox.c")
        source_filename = os.path.join(algorithm_dir, "source.cpp")
        with open(source_filename, "w") as f:
            f.write(self.text)

        cli = [
            "g++",
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

        if not os.path.isfile(executable_filename):
            logger.warning(f"executing an algorithm that did not compile")
            executable_filename = "true"
            connection.error_pipe.write("compilation failed")

        logger.debug("starting process")

        with subprocess.Popen(
                [executable_filename],
                universal_newlines=True,
                stdin=connection.downward_pipe,
                stdout=connection.upward_pipe,
                bufsize=1,
        ) as p:
            yield p

        if p.returncode != 0:
            logger.warning(f"process terminated with returncode {p.returncode}")
            raise AlgorithmRuntimeError("invalid return code {p.returncode}")
