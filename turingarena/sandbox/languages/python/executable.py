import shutil
import pkg_resources

from contextlib import contextmanager
from tempfile import TemporaryDirectory

from turingarena.sandbox.executable import AlgorithmExecutable
from turingarena.sandbox.process import PopenProcess


class PythonAlgorithmExecutableScript(AlgorithmExecutable):
    __slots__ = []

    @contextmanager
    def run(self, connection):
        # get file path
        sandbox_path = pkg_resources.resource_filename(__name__, "sandbox.py")

        # create tmp directory
        with TemporaryDirectory(dir="/tmp", prefix="python_cwd_") as cwd:
            # copy files into tmp dir
            shutil.copy(f"{self.algorithm_dir}/source.py", cwd)
            shutil.copy(f"{self.algorithm_dir}/skeleton.py", cwd)

            # run process
            with PopenProcess.run(
                ["python", sandbox_path],
                universal_newlines=True,
                # preexec_fn=lambda: set_memory_and_time_limits(),
                cwd=cwd,
                stdin=connection.downward,
                stdout=connection.upward,
                bufsize=1,
            ) as process:
                yield process
