import logging
import os
import shutil
import subprocess

import pkg_resources

from turingarena.modules import module_to_python_package
from turingarena.protocol.module import PROTOCOL_QUALIFIER
from turingarena.sandbox.exceptions import CompilationFailed
from turingarena.sandbox.executable import AlgorithmExecutable
from turingarena.sandbox.source import AlgorithmSource

logger = logging.getLogger(__name__)


class CppAlgorithmSource(AlgorithmSource):
    __slots__ = []

    def do_compile(self, *, algorithm_dir, protocol_name, interface_name):
        skeleton_path = pkg_resources.resource_filename(
            module_to_python_package(PROTOCOL_QUALIFIER, protocol_name),
            f"_skeletons/{interface_name}/cpp/skeleton.cpp",
        )

        source_filename = os.path.join(algorithm_dir, "source.cpp")
        with open(source_filename, "w") as f:
            f.write(self.text)

        shutil.copy(skeleton_path, os.path.join(algorithm_dir, "skeleton.cpp"))

        cli = [
            "g++",
            "-o", "algorithm",
            "source.cpp",
            "skeleton.cpp",
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

        return ElfAlgorithmExecutable(algorithm_dir=algorithm_dir)


class ElfAlgorithmExecutable(AlgorithmExecutable):
    __slots__ = []

    def start_os_process(self, connection):
        executable_filename = os.path.join(self.algorithm_dir, "algorithm")

        if not os.path.isfile(executable_filename):
            logger.warning(f"executing an algorithm that did not compile")
            executable_filename = "true"
            connection.error_pipe.write("compilation failed")

        logger.debug("starting process")
        return subprocess.Popen(
            [executable_filename],
            universal_newlines=True,
            stdin=connection.downward_pipe,
            stdout=connection.upward_pipe,
            bufsize=1,
        )
