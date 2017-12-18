import logging
import os
import shutil
import subprocess

import pkg_resources

from turingarena.modules import module_to_python_package
from turingarena.protocol.module import PROTOCOL_QUALIFIER
from turingarena.sandbox.executable import AlgorithmExecutable
from turingarena.sandbox.source import AlgorithmSource

logger = logging.getLogger(__name__)


class CppAlgorithmSource(AlgorithmSource):
    __slots__ = []

    def do_compile(self, algorithm_dir):
        skeleton_path = pkg_resources.resource_filename(
            module_to_python_package(PROTOCOL_QUALIFIER, self.protocol_name),
            f"_skeletons/{self.interface_name}/cpp/skeleton.cpp",
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

        compilation_output_filename = algorithm_dir + "/compilation_output.txt"
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

        with open(algorithm_dir + "/compilation_return.txt", "w") as compilation_return:
            print(compiler.returncode, file=compilation_return)

        if compiler.returncode != 0:
            logger.warning("Compilation failed")

        return ElfAlgorithmExecutable(algorithm_dir=algorithm_dir)


class ElfAlgorithmExecutable(AlgorithmExecutable):
    __slots__ = []

    def start_os_process(self, connection):
        executable_filename = os.path.join(self.algorithm_dir, "algorithm")
        if not os.path.isfile(executable_filename):
            return None

        logger.debug("Starting process")
        return subprocess.Popen(
            [executable_filename],
            universal_newlines=True,
            stdin=connection.downward_pipe,
            stdout=connection.upward_pipe,
            bufsize=1,
        )
