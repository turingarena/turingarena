import logging
import os
import subprocess
from contextlib import contextmanager
from tempfile import TemporaryDirectory

import pkg_resources

from turingarena.sandbox.executable import AlgorithmExecutable
from turingarena.sandbox.rlimits import set_memory_and_time_limits

logger = logging.getLogger(__name__)


class ElfAlgorithmExecutable(AlgorithmExecutable):
    __slots__ = []

    @contextmanager
    def run(self, connection):
        executable_filename = os.path.join(self.algorithm_dir, "algorithm")
        sandbox_path = pkg_resources.resource_filename(__name__, "sandbox.py")

        with TemporaryDirectory(dir="/tmp", prefix="elf_cwd_") as cwd:
            with self.manage_process(
                    subprocess.Popen(
                        ["python3", sandbox_path, executable_filename],
                        universal_newlines=True,
                        preexec_fn=lambda: set_memory_and_time_limits(),
                        cwd=cwd,
                        stdin=connection.downward,
                        stdout=connection.upward,
                        bufsize=1,
                    ),
            ) as process:
                yield process
