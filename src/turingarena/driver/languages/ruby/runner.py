import os
import shutil
from contextlib import contextmanager

import pkg_resources
from turingarena.driver.sandbox.popen import create_popen_process_connection
from turingarena.driver.sandbox.rlimits import set_rlimits
from turingarena.driver.sandbox.runner import ProgramRunner

class RubyProgramRunner(ProgramRunner):
    __slots__ = []

    @property
    def skeleton_path(self):
        return os.path.join(self.temp_dir, "skeleton.rb")

    @contextmanager
    def run_in_process(self):
        shutil.copy(self.program.source_path, self.temp_dir)

        with open(self.skeleton_path, "w") as f:
            self.language.Generator().generate_to_file(self.interface, f)

        os.chmod(self.skeleton_path, 484)
        sandbox_path = pkg_resources.resource_filename(__name__, "sandbox.py")

        yield create_popen_process_connection(
            ["python3", sandbox_path, self.skeleton_path],
            preexec_fn=set_rlimits,
        )
