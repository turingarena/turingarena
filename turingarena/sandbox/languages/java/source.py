import logging
import os
import shutil
import subprocess
from contextlib import contextmanager
from subprocess import CalledProcessError

import pkg_resources

from turingarena.sandbox.exceptions import CompilationFailed
from turingarena.sandbox.process import PopenProcess
from turingarena.sandbox.rlimits import set_memory_and_time_limits
from turingarena.sandbox.source import AlgorithmSource

logger = logging.getLogger(__name__)


class JavaAlgorithmSource(AlgorithmSource):
    __slots__ = []

    def compile(self, compilation_dir):
        # rename files because javac will complain if the file doesn't have
        # the same name of the class defined in it.
        shutil.copy(self.source_path, os.path.join(compilation_dir, "Solution.java"))

        with open(os.path.join(compilation_dir, "Skeleton.java"), "w") as f:
            self.language.skeleton_generator(self.interface).write_to_file(f)

        try:
            subprocess.run(
                [
                    "javac",
                    "Skeleton.java",
                    "Solution.java",
                ],
                cwd=compilation_dir,
                universal_newlines=True,
                bufsize=1,
                check=True,
            )
        except CalledProcessError as e:
            raise CompilationFailed from e

        logger.info("Java file compilation succeded")

    @contextmanager
    def run(self, compilation_dir, connection):
        security_policy_path = pkg_resources.resource_filename(__name__, "security.policy")

        cli = [
            "java",
            "-Djava.security.manager",
            f"-Djava.security.policy=={security_policy_path}",
            "Skeleton",
        ]

        with PopenProcess.run(
                cli,
                universal_newlines=True,
                preexec_fn=lambda: set_memory_and_time_limits(memory_limit=None, time_limit=2),
                cwd=compilation_dir,
                stdin=connection.downward,
                stdout=connection.upward,
                bufsize=1,
        ) as process:
            yield process

    def get_memory_usage(self, process):
        # FIXME: unused
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
