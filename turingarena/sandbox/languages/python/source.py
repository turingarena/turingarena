import logging
import os

from turingarena.common import write_to_file
from turingarena.interface.skeleton.python import generate_skeleton_python
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
