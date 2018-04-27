import os
import shutil
from contextlib import contextmanager

import pkg_resources

from turingarena_impl.sandbox.process import PopenProcess
from turingarena_impl.sandbox.source import AlgorithmSource


class PythonAlgorithmSource(AlgorithmSource):
    __slots__ = []

    def skeleton_path(self, compilation_dir):
        return os.path.join(compilation_dir, "skeleton.py")

    def compile(self, compilation_dir):
        shutil.copy(self.source_path, compilation_dir)

        with open(self.skeleton_path(compilation_dir), "w") as f:
            self.language.skeleton_generator(self.interface).write_to_file(f)

    @contextmanager
    def run(self, compilation_dir, connection):
        sandbox_path = pkg_resources.resource_filename(__name__, "sandbox.py")

        with PopenProcess.run(
                ["python3", sandbox_path, self.source_path, self.skeleton_path(compilation_dir)],
                universal_newlines=True,
                # preexec_fn=lambda: set_memory_and_time_limits(),
                stdin=connection.downward,
                stdout=connection.upward,
                bufsize=1,
        ) as process:
            yield process
