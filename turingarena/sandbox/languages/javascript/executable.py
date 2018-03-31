import shutil
import subprocess
import pkg_resources

from contextlib import contextmanager
from tempfile import TemporaryDirectory

from turingarena.sandbox.executable import AlgorithmExecutable
from turingarena.sandbox.rlimits import set_memory_and_time_limits


class JavaScriptAlgorithmExecutableScript(AlgorithmExecutable):
    __slots__ = []

    @contextmanager
    def run(self, connection):
        sandbox_path = pkg_resources.resource_filename(__name__, "sandbox.js")

        with TemporaryDirectory(dir="/tmp", prefix="javascript_cwd_") as cwd:
            shutil.copy(f"{self.algorithm_dir}/source.js", cwd)
            shutil.copy(f"{self.algorithm_dir}/skeleton.js", cwd)

            process = subprocess.Popen(
                ["node", sandbox_path],
                universal_newlines=True,
                preexec_fn=lambda: set_memory_and_time_limits(memory_limit=None, time_limit=5),
                cwd=cwd,
                stdin=connection.downward,
                stdout=connection.upward,
                bufsize=1,
            )

            with self.manage_process(process) as p:
                yield p
