import logging
import os
import shutil
import subprocess
from contextlib import contextmanager

from turingarena.driver.sandbox.connection import create_failed_connection
from turingarena.driver.sandbox.popen import create_popen_process_connection
from turingarena.driver.sandbox.rlimits import set_rlimits
from turingarena.driver.sandbox.runner import ProgramRunner

logger = logging.getLogger(__name__)


class GoProgramRunner(ProgramRunner):
    @property
    def executable_path(self):
        return os.path.join(self.temp_dir, "algorithm")

    @contextmanager
    def run_in_process(self):
        with open(os.path.join(self.temp_dir, "skeleton.go"), "w") as f:
            self.language.skeleton_generator().generate_to_file(self.interface, f)

        shutil.copyfile(self.program.source_path, os.path.join(self.temp_dir, "solution.go"))

        cli = [
            "go",
            "build",
            "-o", self.executable_path,
            os.path.join(self.temp_dir, "skeleton.go"),
            os.path.join(self.temp_dir, "solution.go"),
        ]
        logger.debug(f"Running {' '.join(cli)}")
        try:
            subprocess.run(
                cli,
                universal_newlines=True,
                check=True,
            )
        except subprocess.CalledProcessError:
            yield create_failed_connection("Compilation failed.")
        else:
            # sandbox_path = pkg_resources.resource_filename(__name__, "sandbox.py")
            yield create_popen_process_connection(
                [self.executable_path],
                preexec_fn=set_rlimits,
            )
