import logging
import os
import shutil
import subprocess
from contextlib import contextmanager
from tempfile import TemporaryDirectory

import pkg_resources

from turingarena.sandbox.exceptions import AlgorithmRuntimeError
from turingarena.sandbox.executable import AlgorithmExecutable
from turingarena.sandbox.rlimits import set_memory_and_time_limits

logger = logging.getLogger(__name__)


class JavaAlgorithmExecutable(AlgorithmExecutable):
    __slots__ = []

    @contextmanager
    def run(self, connection):
        # get class files
        skeleton_path = os.path.join(self.algorithm_dir, "Skeleton.class")
        solution_path = os.path.join(self.algorithm_dir, "Solution.class")
        security_policy_path = pkg_resources.resource_filename(__name__, "security.policy")

        with TemporaryDirectory(dir="/dev/shm", prefix="java_cwd_") as cwd:
            # copy class files to current directory
            shutil.copy(skeleton_path, cwd)
            shutil.copy(solution_path, cwd)
            shutil.copy(security_policy_path, cwd)

            cli = [
                "java",
                "-Djava.security.manager",
                "-Djava.security.policy==security.policy",
                "Skeleton",
            ]

            # run java process 
            with subprocess.Popen(
                    cli,
                    universal_newlines=True,
                    preexec_fn=lambda: set_memory_and_time_limits(memory_limit=None, time_limit=2),
                    cwd=cwd,
                    stdin=connection.downward,
                    stdout=connection.upward,
                    bufsize=1,
            ) as p:
                logger.debug(f"starting process")
                yield p
                logger.debug(f"waiting for process")

            if p.returncode != 0:
                logger.warning(f"process terminated with returncode {p.returncode}")
                raise AlgorithmRuntimeError(f"invalid return code {p.returncode}", "")
