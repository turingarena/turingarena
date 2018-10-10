import os
import shutil
from contextlib import contextmanager

from turingarena_impl.driver.sandbox.process import PopenProcess
from turingarena_impl.driver.sandbox.rlimits import set_memory_and_time_limits
from turingarena_impl.driver.source import AlgorithmSource


class BashAlgorithmSource(AlgorithmSource):
    def skeleton_path(self, compilation_dir):
        return os.path.join(compilation_dir, "skeleton.sh")

    def compile(self, compilation_dir):
        shutil.copy(self.source_path, os.path.join(compilation_dir, "solution.sh"))

        with open(self.skeleton_path(compilation_dir), "w") as f:
            self.language.skeleton_generator().generate_to_file(self.interface, f)


    @contextmanager
    def run(self, compilation_dir, connection):
        os.chdir(compilation_dir)
        with PopenProcess.run(
                ["bash", self.skeleton_path(compilation_dir)],
                universal_newlines=True,
                preexec_fn=lambda: set_memory_and_time_limits(),
                stdin=connection.downward,
                stdout=connection.upward,
                bufsize=1,
        ) as process:
            yield process

