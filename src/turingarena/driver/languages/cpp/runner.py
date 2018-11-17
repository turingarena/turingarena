import logging
import os
import subprocess
from contextlib import contextmanager
from subprocess import CalledProcessError

import pkg_resources
from turingarena.driver.sandbox.connection import create_failed_connection
from turingarena.driver.sandbox.popen import create_popen_process_connection
from turingarena.driver.sandbox.rlimits import set_rlimits
from turingarena.driver.sandbox.runner import ProgramRunner


class CppProgramRunner(ProgramRunner):
    @contextmanager
    def run_in_process(self):
        with open(self._skeleton_path, "w") as f:
            self.language.skeleton_generator().generate_to_file(self.interface, f)

        try:
            self._compile_source()
            self._compile_skeleton()
            self._link_executable()
        except CalledProcessError:
            yield create_failed_connection("Compilation failed.")
        else:
            sandbox_path = pkg_resources.resource_filename(__name__, "sandbox.py")

            yield create_popen_process_connection(
                ["python3", sandbox_path, self.executable_path],
                preexec_fn=set_rlimits,
            )

    def _compile_source(self):
        cli = [
            "g++", "-c", "-O2", "-std=c++17", "-Wall",
            "-o", self._source_object_path,
            self.program.source_path
        ]

        logging.debug("Compiling source: " + " ".join(cli))
        subprocess.run(cli, universal_newlines=True, check=True)

    def _compile_skeleton(self):
        cli = [
            "g++", "-c", "-O2", "-std=c++17", "-Wno-unused-result",
            "-o", self._skeleton_object_path,
            self._skeleton_path,
        ]

        logging.debug("Compiling skeleton: " + " ".join(cli))
        subprocess.run(cli, universal_newlines=True, check=True)

    def _link_executable(self):
        cli = [
            "g++", "-static",
            "-o", self.executable_path,
            self._skeleton_object_path,
            self._source_object_path
        ]

        logging.debug("Linking executable: " + " ".join(cli))
        subprocess.run(cli, universal_newlines=True, check=True)

    @property
    def executable_path(self):
        return os.path.join(self.temp_dir, "algorithm")

    @property
    def _skeleton_path(self):
        return os.path.join(self.temp_dir, "skeleton.cpp")

    @property
    def _skeleton_object_path(self):
        return os.path.join(self.temp_dir, "skeleton.o")

    @property
    def _source_object_path(self):
        return os.path.join(self.temp_dir, "source.o")
