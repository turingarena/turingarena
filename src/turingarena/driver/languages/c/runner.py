import os
import logging
import subprocess

from turingarena.driver.languages.cpp.runner import CppProgramRunner

logger = logging.getLogger(__name__)


class CProgramRunner(CppProgramRunner):
    def _compile_source(self):
        cli = [
            *self._ccache(), "gcc", "-c", "-O2", "-std=gnu11", "-Wall",
            "-o", self._source_object_path,
            self.program.source_path,
        ]

        logger.debug("Compiling source: " + " ".join(cli))
        subprocess.run(cli, universal_newlines=True, check=True)

    def _compile_skeleton(self):
        cli = [
            *self._ccache(), "gcc", "-c", "-O2", "-std=gnu11", "-Wno-unused-result",
            "-o", self._skeleton_object_path,
            self._skeleton_path,
        ]

        logging.debug("Compiling skeleton: " + " ".join(cli))
        subprocess.run(cli, universal_newlines=True, check=True)

    def _link_executable(self):
        cli = [
            *self._ccache(), "gcc", "-static",
            "-o", self.executable_path,
            self._skeleton_object_path,
            self._source_object_path,
        ]

        logging.debug("Linking executable: " + " ".join(cli))
        subprocess.run(cli, universal_newlines=True, check=True)

    @property
    def _skeleton_path(self):
        return os.path.join(self.temp_dir, "skeleton.c")
