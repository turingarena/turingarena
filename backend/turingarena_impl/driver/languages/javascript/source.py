import os
from contextlib import contextmanager

import pkg_resources

from turingarena_impl.driver.sandbox.process import PopenProcess
from turingarena_impl.driver.sandbox.rlimits import set_memory_and_time_limits
from turingarena_impl.driver.source import AlgorithmSource


class JavascriptAlgorithmSource(AlgorithmSource):
    __slots__ = []

    def compile(self, compilation_dir):
        with open(self.skeleton_path(compilation_dir), "w") as f:
            self.language.skeleton_generator().generate_to_file(self.interface, f)

    def skeleton_path(self, compilation_dir):
        return os.path.join(compilation_dir, "skeleton.js")

    @contextmanager
    def run(self, compilation_dir, connection):
        sandbox_path = pkg_resources.resource_filename(__name__, "sandbox.js")

        with PopenProcess.run(
                ["node", sandbox_path, self.source_path, self.skeleton_path(compilation_dir)],
                universal_newlines=True,
                preexec_fn=lambda: set_memory_and_time_limits(memory_limit=None, time_limit=5),
                stdin=connection.downward,
                stdout=connection.upward,
                bufsize=1,
        ) as process:
            yield process
