import os
import shutil
from contextlib import contextmanager

import pkg_resources
from turingarena_impl.driver.sandbox.popen import create_popen_process_connection
from turingarena_impl.driver.sandbox.rlimits import set_rlimits
from turingarena_impl.driver.sandbox.runner import ProgramRunner


class PythonProgramRunner(ProgramRunner):
    __slots__ = []

    @property
    def skeleton_path(self):
        return os.path.join(self.temp_dir, "skeleton.py")

    @contextmanager
    def run_in_process(self):
        shutil.copy(self.program.source_path, self.temp_dir)

        with open(self.skeleton_path, "w") as f:
            self.language.skeleton_generator().generate_to_file(self.interface, f)

        sandbox_path = pkg_resources.resource_filename(__name__, "sandbox.py")

        yield create_popen_process_connection(
            ["python3", sandbox_path, self.program.source_path, self.skeleton_path],
            preexec_fn=set_rlimits,
        )
