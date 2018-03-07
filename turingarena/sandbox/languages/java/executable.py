import logging
import os
import resource
import subprocess
from contextlib import contextmanager
from tempfile import TemporaryDirectory
import shutil

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

        with TemporaryDirectory(dir="/dev/shm", prefix="java_cwd_") as cwd:

            # copy class files to current directory 
            shutil.copy(skeleton_path, cwd)
            shutil.copy(solution_path, cwd)

            # run java process 
            with subprocess.Popen(
                    ["java", "Solution"],
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
                raise AlgorithmRuntimeError(f"invalid return code {p.returncode}")

def set_memory_and_time_limits():
    memory_limit = 16 * 1024 * 1024
    time_limit = 1
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
    resource.setrlimit(
        resource.RLIMIT_AS,
        (memory_limit, resource.RLIM_INFINITY),
    )
