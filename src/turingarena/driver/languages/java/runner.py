import logging
import os
import shutil
import subprocess
from contextlib import contextmanager
from subprocess import CalledProcessError

import pkg_resources
from turingarena.driver.sandbox.connection import create_failed_connection
from turingarena.driver.sandbox.popen import create_popen_process_connection
from turingarena.driver.sandbox.runner import ProgramRunner

logger = logging.getLogger(__name__)


class JavaProgramRunner(ProgramRunner):
    __slots__ = []

    @property
    def skeleton_path(self):
        return os.path.join(self.temp_dir, "Skeleton.java")

    @contextmanager
    def run_in_process(self):
        # rename files because javac will complain if the file doesn't have
        # the same name of the class defined in it.
        solution_path = os.path.join(self.temp_dir, "Solution.java")
        shutil.copy(self.program.source_path, solution_path)

        with open(self.skeleton_path, "w") as f:
            self.language.Generator().generate_to_file(self.interface, f)

        try:
            subprocess.run(
                [
                    "javac",
                    self.skeleton_path,
                    solution_path,
                ],
                universal_newlines=True,
                bufsize=1,
                check=True,
            )
        except CalledProcessError:
            yield create_failed_connection("Compilation failed.")
        else:
            security_policy_path = pkg_resources.resource_filename(__name__, "security.policy")
            cli = [
                "java",
                "-cp", self.temp_dir,
                "-Djava.security.manager",
                f"-Djava.security.policy=={security_policy_path}",
                "Skeleton",
            ]

            yield create_popen_process_connection(
                cli,
                # preexec_fn=set_rlimits(),
            )

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
