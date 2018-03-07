import logging
import os
import subprocess
from subprocess import CalledProcessError

from turingarena.common import write_to_file
from turingarena.protocol.skeleton.java import generate_skeleton_java
from turingarena.sandbox.exceptions import CompilationFailed
from turingarena.sandbox.source import AlgorithmSource

logger = logging.getLogger(__name__)

class JavaAlgorithmSource(AlgorithmSource):
    __slots__ = []

    def do_compile(self, algorithm_dir):
        
        # get files 
        skeleton_filename = os.path.join(algorithm_dir, "Skeleton.java")
        solution_filename = os.path.join(algorithm_dir, "Solution.java")

        with open(skeleton_filename, "w") as f:
            write_to_file(generate_skeleton_java(self.interface), f)

        with open(solution_filename, "w") as f:
            f.write(self.text)

        cli = [
            "javac",
            "Skeleton.java", 
            "Solution.java"
        ]
        logger.debug(f"Running {' '.join(cli)}")

        try:
            subprocess.run(
                cli,
                cwd=algorithm_dir,
                universal_newlines=True,
                check=True,
            )
        except CalledProcessError as e:
            if e.returncode == 1:
                raise CompilationFailed
            raise
        
        logger.info("Java file compilation succeded")
