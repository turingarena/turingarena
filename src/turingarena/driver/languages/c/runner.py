import logging
import subprocess

from turingarena.driver.languages.cpp.runner import CppProgramRunner

logger = logging.getLogger(__name__)


class CProgramRunner(CppProgramRunner):
    def _compile_source(self):
        cli = [
            "gcc", "-c", "-O2", "-std=c11", "-Wall",
            "-o", self._source_object_path,
            self.program.source_path
        ]

        logger.debug("Compiling source: " + " ".join(cli))
        subprocess.run(cli, universal_newlines=True, check=True)
