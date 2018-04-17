import os
import shutil
from contextlib import contextmanager
from tempfile import TemporaryDirectory

import pkg_resources

from turingarena.sandbox.process import PopenProcess
from turingarena.sandbox.rlimits import set_memory_and_time_limits
from turingarena.sandbox.source import AlgorithmSource


class JavascriptAlgorithmSource(AlgorithmSource):
    __slots__ = []

    @contextmanager
    def run(self, connection):
        sandbox_path = pkg_resources.resource_filename(__name__, "sandbox.js")

        with TemporaryDirectory(dir="/tmp", prefix="javascript_cwd_") as cwd:
            shutil.copy(self.source_path, cwd)

            with open(os.path.join(cwd, f"skeleton{self.language.extension}"), "w") as f:
                self.language.skeleton_generator(self.interface).write_to_file(f)

            with PopenProcess.run(
                    ["node", sandbox_path],
                    universal_newlines=True,
                    preexec_fn=lambda: set_memory_and_time_limits(memory_limit=None, time_limit=5),
                    cwd=cwd,
                    stdin=connection.downward,
                    stdout=connection.upward,
                    bufsize=1,
            ) as process:
                yield process
