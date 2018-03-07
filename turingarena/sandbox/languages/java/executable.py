import logging
import os
import resource
import shutil
import subprocess
from contextlib import contextmanager
from tempfile import TemporaryDirectory

import pkg_resources

from turingarena.sandbox.exceptions import AlgorithmRuntimeError
from turingarena.sandbox.executable import AlgorithmExecutable

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

            # run java process 
            with subprocess.Popen(
                    [
                        "java",
                        "-Djava.security.manager",
                        "-Djava.security.policy==security.policy",
                        "-Xmx64m",  # FIXME: is this sufficient to limit memory?
                        "-Xss64m",
                        "Skeleton",
                    ],
                    universal_newlines=True,
                    preexec_fn=set_memory_and_time_limits,
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


def set_memory_and_time_limits():
    time_limit = 2
    core_limit = 32 * 1024 * 1024

    resource.setrlimit(
        resource.RLIMIT_CORE,
        (core_limit, resource.RLIM_INFINITY),
    )
    resource.setrlimit(
        resource.RLIMIT_STACK,
        (resource.RLIM_INFINITY, resource.RLIM_INFINITY),
    )
    resource.setrlimit(
        resource.RLIMIT_CPU,
        (time_limit, resource.RLIM_INFINITY),
        # use soft < hard to ensure SIGXCPU is raised instead of SIGKILL
        # see setrlimit(2)
    )
    if False:  # FIXME: seems to kill the JVM
        memory_limit = 256 * 1024 * 1024
        resource.setrlimit(
            resource.RLIMIT_AS,
            (memory_limit, resource.RLIM_INFINITY),
        )
