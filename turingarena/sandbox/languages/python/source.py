import os
import shutil
from contextlib import contextmanager
from tempfile import TemporaryDirectory

import pkg_resources

from turingarena.sandbox.process import PopenProcess
from turingarena.sandbox.source import AlgorithmSource


class PythonAlgorithmSource(AlgorithmSource):
    __slots__ = []

    @contextmanager
    def run(self, connection):
        sandbox_path = pkg_resources.resource_filename(__name__, "sandbox.py")

        with TemporaryDirectory(dir="/tmp", prefix="python_cwd_") as cwd:
            shutil.copy(self.source_path, cwd)

            with open(os.path.join(cwd, f"skeleton.py"), "w") as f:
                self.language.skeleton_generator(self.interface).write_to_file(f)

            # run process
            with PopenProcess.run(
                    ["python", sandbox_path, self.source_path, "skeleton.py"],
                    universal_newlines=True,
                    # preexec_fn=lambda: set_memory_and_time_limits(),
                    cwd=cwd,
                    stdin=connection.downward,
                    stdout=connection.upward,
                    bufsize=1,
            ) as process:
                yield process
