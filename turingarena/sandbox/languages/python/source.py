import os
import shutil
from contextlib import contextmanager

import pkg_resources

from turingarena.sandbox.process import PopenProcess
from turingarena.sandbox.source import AlgorithmSource


class PythonAlgorithmSource(AlgorithmSource):
    __slots__ = []

    def compile(self, compilation_dir):
        shutil.copy(self.source_path, compilation_dir)

        with open(os.path.join(compilation_dir, f"skeleton.py"), "w") as f:
            self.language.skeleton_generator(self.interface).write_to_file(f)

    @contextmanager
    def run(self, compilation_dir, connection):
        sandbox_path = pkg_resources.resource_filename(__name__, "sandbox.py")

        with PopenProcess.run(
                ["python", sandbox_path, self.source_path, "skeleton.py"],
                universal_newlines=True,
                # preexec_fn=lambda: set_memory_and_time_limits(),
                cwd=compilation_dir,
                stdin=connection.downward,
                stdout=connection.upward,
                bufsize=1,
        ) as process:
            yield process
