import logging
import os
import shutil
import subprocess
from contextlib import contextmanager
from tempfile import TemporaryDirectory

import pkg_resources

from turingarena.sandbox.exceptions import AlgorithmRuntimeError
from turingarena.sandbox.executable import AlgorithmExecutable

logger = logging.getLogger(__name__)


class JavaScriptAlgorithmExecutableScript(AlgorithmExecutable):
    __slots__ = []

    @contextmanager
    def run(self, connection):
        # get file path
        sandbox_path = pkg_resources.resource_filename(__name__, "sandbox.js")
        source_path = os.path.join(self.algorithm_dir, "source.js")
        skeleton_path = os.path.join(self.algorithm_dir, "skeleton.js")

        # create tmp directory
        with TemporaryDirectory(dir="/dev/shm", prefix="javascript_cwd_") as cwd:
            # copy files into tmp dir
            shutil.copy(sandbox_path, cwd)
            shutil.copy(source_path, cwd)
            shutil.copy(skeleton_path, cwd)

            # run process
            with subprocess.Popen(
                    ["node", "sandbox.js"],
                    universal_newlines=True,
                    # preexec_fn=set_memory_and_time_limits,
                    cwd=cwd,
                    stdin=connection.downward,
                    stdout=connection.upward,
                    bufsize=1,
            ) as p:
                logger.debug(f"starting process")
                yield p
                logger.debug(f"waiting for process")

            # check return code
            if p.returncode != 0:
                logger.warning(f"process terminated with returncode {p.returncode}")
                raise AlgorithmRuntimeError(f"invalid return code {p.returncode}", "")
