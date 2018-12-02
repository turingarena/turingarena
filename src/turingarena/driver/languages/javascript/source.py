import os

import pkg_resources
from turingarena.driver.sandbox.process import PopenProcess
from turingarena.driver.source import AlgorithmSource

from turingarena.driver.sandbox.rlimits import set_rlimits


class JavascriptAlgorithmSource(AlgorithmSource):
    __slots__ = []

    def compile(self, compilation_dir):
        with open(self.skeleton_path(compilation_dir), "w") as f:
            self.language.Generator().generate_to_file(self.interface, f)

    def skeleton_path(self, compilation_dir):
        return os.path.join(compilation_dir, "skeleton.js")

    def create_process(self, compilation_dir, connection):
        sandbox_path = pkg_resources.resource_filename(__name__, "sandbox.js")

        return PopenProcess(
            connection,
            ["node", sandbox_path, self.program.source_path, self.skeleton_path(compilation_dir)],
            preexec_fn=set_rlimits,
        )
