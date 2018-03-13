import logging
import os
import shutil
import subprocess
from contextlib import contextmanager
from tempfile import TemporaryDirectory

import pkg_resources

from turingarena.sandbox.executable import AlgorithmExecutable
from turingarena.sandbox.rlimits import set_memory_and_time_limits

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
        with TemporaryDirectory(dir="/tmp", prefix="javascript_cwd_") as cwd:
            # copy files into tmp dir
            shutil.copy(sandbox_path, cwd)
            shutil.copy(source_path, cwd)
            shutil.copy(skeleton_path, cwd)

            popen = subprocess.Popen(
                ["node", "sandbox.js"],
                universal_newlines=True,
                preexec_fn=lambda : set_memory_and_time_limits(memory_limit=None, time_limit=5),
                cwd=cwd,
                stdin=connection.downward,
                stdout=connection.upward,
                bufsize=1,
            )
            # run process
            with self.manage_process(popen) as p:
                yield p
