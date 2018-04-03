import logging
import subprocess
import shutil

from turingarena.sandbox.exceptions import CompilationFailed
from turingarena.sandbox.source import AlgorithmSource

logger = logging.getLogger(__name__)


class JavaAlgorithmSource(AlgorithmSource):
    __slots__ = []

    def do_compile(self, algorithm_dir):

        # rename files because javac will complain if the file doesn't have
        # the same name of the class defined in it. 
        shutil.move(f"{algorithm_dir}/source.java", f"{algorithm_dir}/Solution.java")
        shutil.move(f"{algorithm_dir}/skeleton.java", f"{algorithm_dir}/Skeleton.java")

        cli = [
            "javac",
            "Skeleton.java", 
            "Solution.java"
        ]

        logger.debug(f"Running {' '.join(cli)}")

        with subprocess.Popen(
                cli,
                cwd=algorithm_dir,
                universal_newlines=True,
                stderr=subprocess.PIPE,
                bufsize=1
        ) as p:
            p.wait()
            if p.returncode != 0:
                out = p.communicate()[1]
                raise CompilationFailed(out)
        
        logger.info("Java file compilation succeded")
