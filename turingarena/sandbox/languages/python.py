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
        protocol, interface_name = self.interface.split(":")
        skeleton_path = pkg_resources.resource_filename(
            module_to_python_package(PROTOCOL_QUALIFIER, protocol),
            f"_skeletons/{interface_name}/python/skeleton.py",
        )

        source_filename = os.path.join(algorithm_dir, "source.py")
        with open(source_filename, "w") as f:
            f.write(self.text)

        shutil.copy(skeleton_path, os.path.join(algorithm_dir, "skeleton.py"))


class PythonAlgorithmExecutableScript(AlgorithmExecutable):
    __slots__ = []

    def start_os_process(self, connection):
        executable_filename = os.path.join(self.algorithm_dir, "skeleton.py")

        logger.debug("invoking python interpreter")
        return subprocess.Popen(
            ["python3.6", executable_filename],
            universal_newlines=True,
            stdin=connection.downward_pipe,
            stdout=connection.upward_pipe,
            bufsize=1,
        )
