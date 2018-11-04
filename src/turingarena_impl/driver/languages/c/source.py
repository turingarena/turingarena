import logging
import subprocess

from turingarena_impl.driver.languages.cpp import CppAlgorithmSource

logger = logging.getLogger(__name__)


class CAlgorithmSource(CppAlgorithmSource):
    def _compile_source(self, compilation_dir):
        cli = [
            "gcc", "-c", "-O2", "-std=c11", "-Wall",
            "-o", self._source_object_path(compilation_dir),
            self.source_path
        ]

        logger.debug("Compiling source: " + " ".join(cli))
        subprocess.run(cli, universal_newlines=True, check=True)
