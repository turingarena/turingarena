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


class PythonAlgorithmSource(AlgorithmSource):
    __slots__ = []

    def do_compile(self, algorithm_dir):
        skeleton_path = pkg_resources.resource_filename(
            module_to_python_package(PROTOCOL_QUALIFIER, self.protocol_name),
            f"_skeletons/{self.interface_name}/python/skeleton.py",
        )

        source_filename = os.path.join(algorithm_dir, "source.py")
        with open(source_filename, "w") as f:
            f.write(self.text)

        shutil.copy(skeleton_path, os.path.join(algorithm_dir, "skeleton.py"))

        cli = [
            "python",
            "-m", "py_compile",
            "source.py",
        ]
        logger.debug(f"Running {' '.join(cli)}")

        execution_output_filename = os.path.join(algorithm_dir, "execution_output.txt")
        with open(execution_output_filename, "w") as execution_output:
            compiler = subprocess.run(
                cli,
                cwd=algorithm_dir,
                stderr=execution_output,
                universal_newlines=True,
            )
        with open(execution_output_filename) as execution_output:
            for line in execution_output:
                logger.debug(f"py_compile: {line.rstrip()}")

        if compiler.returncode == 0:
            logger.info("execution successful")
        elif compiler.returncode == 1:
            logger.warning("execution failed")
        else:
            raise ValueError("Unable to invoke py_compile properly")

        #shutil.copy(algorithm_dir + "/source.py", "algorithm")

        return PythonAlgorithmExecutableScript(algorithm_dir=algorithm_dir)


class PythonAlgorithmExecutableScript(AlgorithmExecutable):
    __slots__ = []

    def start_os_process(self, connection):
        executable_filename = os.path.join(self.algorithm_dir, "skeleton.py")

        if not os.path.isfile(executable_filename):
            logger.warning(f"executing an algorithm that did not compile")
            executable_filename = "true"
            connection.error_pipe.write("compilation failed")

        logger.debug("starting process")
        return subprocess.Popen(
            ["python", executable_filename],
            universal_newlines=True,
            stdin=connection.downward_pipe,
            stdout=connection.upward_pipe,
            bufsize=1,
        )
