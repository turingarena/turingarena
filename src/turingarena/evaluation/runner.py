import os
import subprocess
from abc import abstractmethod
from collections import namedtuple
from contextlib import contextmanager
from tempfile import TemporaryDirectory


class EvaluatorParameters:
    def __init__(self, params):
        self._params = params

    def __getattr__(self, item):
        return self._params.get(item)


class EvaluatorRunner(namedtuple("EvaluatorRunner", ["cwd", "path", "params"])):
    @abstractmethod
    def perform_run(self):
        """
        Returns a contextmanager which prepares the execution and gives the command to run.
        """


class PythonEvaluatorRunner(EvaluatorRunner):
    @contextmanager
    def perform_run(self):
        yield [
            self.params.python_executable or "python3",
            "-u",
            "evaluator.py",
        ]


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
        return ["bash", "evaluator.sh"]


evaluator_runner_by_extension = {
    ".py": PythonEvaluatorRunner,
    ".cpp": CppEvaluatorRunner,
    ".sh": BashEvaluatorRunner,
}
