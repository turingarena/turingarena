import os
import shutil
from contextlib import contextmanager

from turingarena.driver.sandbox.popen import create_popen_process_connection
from turingarena.driver.sandbox.rlimits import set_rlimits
from turingarena.driver.sandbox.runner import ProgramRunner


class BashProgramRunner(ProgramRunner):
    @property
    def skeleton_path(self):
        return os.path.join(self.temp_dir, "skeleton.sh")

    @contextmanager
    def run_in_process(self):
        shutil.copy(self.program.source_path, os.path.join(self.temp_dir, "solution.sh"))

        with open(self.skeleton_path, "w") as f:
            self.language.skeleton_generator().generate_to_file(self.interface, f)

        yield create_popen_process_connection(
            ["bash", self.skeleton_path],
            cwd=self.temp_dir,
            preexec_fn=set_rlimits,
        )
