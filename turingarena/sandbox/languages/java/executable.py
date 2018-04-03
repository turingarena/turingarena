import logging
import os
import shutil
import subprocess
import pkg_resources

from contextlib import contextmanager
from tempfile import TemporaryDirectory

from turingarena.sandbox.executable import AlgorithmExecutable
from turingarena.sandbox.rlimits import set_memory_and_time_limits

logger = logging.getLogger(__name__)


class JavaAlgorithmExecutable(AlgorithmExecutable):
    __slots__ = []

    @contextmanager
    def run(self, connection):
        # get class files
        security_policy_path = pkg_resources.resource_filename(__name__, "security.policy")

        with TemporaryDirectory(dir="/tmp", prefix="java_cwd_") as cwd:
            # copy all .class file in cwd: need to copy all files because of inner classes!
            for name in os.listdir(self.algorithm_dir):
                if name.endswith(".class"):
                    shutil.copy(os.path.join(self.algorithm_dir, name), cwd)

            cli = [
                "java",
                "-Djava.security.manager",
                f"-Djava.security.policy=={security_policy_path}",
                "Skeleton",
            ]

            process = subprocess.Popen(
                cli,
                universal_newlines=True,
                preexec_fn=lambda: set_memory_and_time_limits(memory_limit=None, time_limit=2),
                cwd=cwd,
                stdin=connection.downward,
                stdout=connection.upward,
                bufsize=1,
            )

            with self.manage_process(process) as p:
                yield p

    def get_memory_usage(self, process):
        cmd = [
            'bash', '-c',
            "jcmd Skeleton GC.class_histogram | tail -n 1 | awk '{print $3}'"
        ]
        try:
            memory_utilization = int(subprocess.check_output(cmd))
        except ValueError:
            memory_utilization = 0
        logger.debug(f"memory usage : {memory_utilization / 1000000}Mb")
        return memory_utilization
