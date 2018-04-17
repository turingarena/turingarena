import os
from contextlib import contextmanager

import pkg_resources

from turingarena.sandbox.process import PopenProcess
from turingarena.sandbox.rlimits import set_memory_and_time_limits
from turingarena.sandbox.source import AlgorithmSource


class JavascriptAlgorithmSource(AlgorithmSource):
    __slots__ = []

    def compile(self, compilation_dir):
        with open(os.path.join(compilation_dir, "skeleton.js"), "w") as f:
            self.language.skeleton_generator(self.interface).write_to_file(f)

    @contextmanager
    def run(self, compilation_dir, connection):
        sandbox_path = pkg_resources.resource_filename(__name__, "sandbox.js")

        with PopenProcess.run(
                ["node", sandbox_path, self.source_path],
                universal_newlines=True,
                preexec_fn=lambda: set_memory_and_time_limits(memory_limit=None, time_limit=5),
                cwd=compilation_dir,
                stdin=connection.downward,
                stdout=connection.upward,
                bufsize=1,
        ) as process:
            yield process
