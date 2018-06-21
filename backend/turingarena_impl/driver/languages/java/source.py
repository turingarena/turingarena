import logging
import os
import shutil
import subprocess
from contextlib import contextmanager
from subprocess import CalledProcessError

import pkg_resources

from turingarena_impl.driver.sandbox.process import PopenProcess
from turingarena_impl.driver.sandbox.rlimits import set_memory_and_time_limits
from turingarena_impl.driver.source import AlgorithmSource, CompilationFailed

logger = logging.getLogger(__name__)


class JavaAlgorithmSource(AlgorithmSource):
    __slots__ = []

    def compile(self, compilation_dir):
        # rename files because javac will complain if the file doesn't have
        # the same name of the class defined in it.
        solution_path = os.path.join(compilation_dir, "Solution.java")
        shutil.copy(self.source_path, solution_path)

        skeleton_path = self.skeleton_path(compilation_dir)
        with open(skeleton_path, "w") as f:
            self.language.skeleton_generator().generate_to_file(self.interface, f)

        try:
            subprocess.run(
                [
                    "javac",
                    skeleton_path,
                    solution_path,
                ],
                universal_newlines=True,
                bufsize=1,
                check=True,
            )
        except CalledProcessError as e:
            raise CompilationFailed from e

        logger.info("Java file compilation succeded")

    def skeleton_path(self, compilation_dir):
        return os.path.join(compilation_dir, "Skeleton.java")

    @contextmanager
    def run(self, compilation_dir, connection):
        security_policy_path = pkg_resources.resource_filename(__name__, "security.policy")

        cli = [
            "java",
            "-cp", compilation_dir,
            "-Djava.security.manager",
            f"-Djava.security.policy=={security_policy_path}",
            "Skeleton",
        ]

        with PopenProcess.run(
                cli,
                universal_newlines=True,
                preexec_fn=lambda: set_memory_and_time_limits(memory_limit=None, time_limit=2),
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
