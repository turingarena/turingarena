import os
import shutil

from turingarena_impl.driver.sandbox.process import PopenProcess
from turingarena_impl.driver.sandbox.rlimits import set_rlimits
from turingarena_impl.driver.source import AlgorithmSource


class BashAlgorithmSource(AlgorithmSource):
    def skeleton_path(self, compilation_dir):
        return os.path.join(compilation_dir, "skeleton.sh")

    def compile(self, compilation_dir):
        shutil.copy(self.source_path, os.path.join(compilation_dir, "solution.sh"))

        with open(self.skeleton_path(compilation_dir), "w") as f:
            self.language.skeleton_generator().generate_to_file(self.interface, f)

    def create_process(self, compilation_dir, connection):
        os.chdir(compilation_dir)
        return PopenProcess(
            connection,
            ["bash", self.skeleton_path(compilation_dir)],
            preexec_fn=set_rlimits,
        )
