import os
import shutil

import pkg_resources

from turingarena_impl.driver.sandbox.process import PopenProcess
from turingarena_impl.driver.sandbox.rlimits import set_rlimits
from turingarena_impl.driver.source import AlgorithmSource


class PythonAlgorithmSource(AlgorithmSource):
    __slots__ = []

    def skeleton_path(self, compilation_dir):
        return os.path.join(compilation_dir, "skeleton.py")

    def compile(self, compilation_dir):
        shutil.copy(self.source_path, compilation_dir)

        with open(self.skeleton_path(compilation_dir), "w") as f:
            self.language.skeleton_generator().generate_to_file(self.interface, f)

    def create_process(self, compilation_dir, connection):
        sandbox_path = pkg_resources.resource_filename(__name__, "sandbox.py")

        return PopenProcess(
            connection,
            ["python3", sandbox_path, self.source_path, self.skeleton_path(compilation_dir)],
            preexec_fn=set_rlimits,
        )
