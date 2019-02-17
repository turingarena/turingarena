import logging
import os
import shutil
import subprocess

from contextlib import contextmanager

from turingarena.driver.sandbox.connection import create_failed_connection
from turingarena.driver.sandbox.popen import create_popen_process_connection
from turingarena.driver.sandbox.rlimits import set_rlimits
from turingarena.driver.sandbox.runner import ProgramRunner


class RustProgramRunner(ProgramRunner):
    @contextmanager
    def run_in_process(self):
        with open(self._skeleton_path, "w") as f:
            self.language.Generator().generate_to_file(self.interface, f)

        shutil.copy(self.program.source_path, self._source_path)

        try:
            self._compile()
        except subprocess.CalledProcessError:
            yield create_failed_connection("Compilation failed.")
        else:
            yield create_popen_process_connection(
                [self.executable_path],
                preexec_fn=set_rlimits,
            )

    def _compile(self):
        cli = [
            "rustc",
            "-o", self.executable_path,
            self._skeleton_path
        ]

        logging.debug("Compiling source: " + " ".join(cli))
        subprocess.run(cli, universal_newlines=True, check=True)

    @property
    def executable_path(self):
        return os.path.join(self.temp_dir, "algorithm")

    @property
    def _skeleton_path(self):
        return os.path.join(self.temp_dir, "skeleton.rs")

    @property
    def _source_path(self):
        return os.path.join(self.temp_dir, "solution.rs")
