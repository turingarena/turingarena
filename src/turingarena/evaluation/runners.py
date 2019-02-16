import os
import subprocess
from contextlib import contextmanager
from tempfile import TemporaryDirectory

from turingarena.evaluation.python.runner import PythonEvaluatorRunner
from turingarena.evaluation.runner import EvaluatorRunner


class CppEvaluatorRunner(EvaluatorRunner):
    @contextmanager
    def perform_run(self):
        with TemporaryDirectory() as compilation_dir:
            executable_path = os.path.join(compilation_dir, "evaluator")
            cli = [
                "g++",
                *(self.params.cpp_flags.split() or [
                    f"-std={self.params.cpp_std or 'c++14'}",
                    "-Wall",
                ]),
                "-o",
                executable_path,
                "evaluator.cpp",
            ]
            subprocess.run(cli, check=True)
            return [executable_path]


class BashEvaluatorRunner(EvaluatorRunner):
    @contextmanager
    def perform_run(self):
        yield ["bash", "evaluator.sh"]


evaluator_runner_by_extension = {
    ".py": PythonEvaluatorRunner,
    ".cpp": CppEvaluatorRunner,
    ".sh": BashEvaluatorRunner,
}
