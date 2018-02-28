import logging
import os
import subprocess
from contextlib import contextmanager

from turingarena.common import write_to_file
from turingarena.protocol.skeleton.python import generate_skeleton_python
from turingarena.sandbox.executable import AlgorithmExecutable
from turingarena.sandbox.source import AlgorithmSource

logger = logging.getLogger(__name__)


class PythonAlgorithmSource(AlgorithmSource):
    __slots__ = []

    def do_compile(self, algorithm_dir):
        source_filename = os.path.join(algorithm_dir, "source.py")
        with open(source_filename, "w") as f:
            f.write(self.text)

        skeleton_filename = os.path.join(algorithm_dir, "skeleton.py")
        with open(skeleton_filename, "w") as f:
            write_to_file(generate_skeleton_python(self.interface), f)


class PythonAlgorithmExecutableScript(AlgorithmExecutable):
    __slots__ = []

    @contextmanager
    def run(self, connection):
        executable_filename = os.path.join(self.algorithm_dir, "skeleton.py")

        logger.debug("invoking python interpreter")
        with subprocess.Popen(
                ["python3.6", executable_filename],
                universal_newlines=True,
                stdin=connection.downward,
                stdout=connection.upward,
                bufsize=1,
        ) as p:
            yield p
