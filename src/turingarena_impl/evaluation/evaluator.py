import logging
import os
import random
import subprocess
from abc import abstractmethod
from collections import namedtuple
from contextlib import ExitStack, contextmanager
from tempfile import TemporaryDirectory

from turingarena import load_metadata
from turingarena_impl.evaluation.segi import segi_subprocess


class Evaluator(namedtuple("Evaluator", ["path"])):
    def _find_evaluators(self):
        filenames = os.listdir(self.path)
        for ext in evaluator_runner_by_extension:
            filename = f"evaluator{ext}"
            if filename in filenames:
                yield filename

    def _find_evaluator(self):
        paths = list(self._find_evaluators())
        if len(paths) > 1:
            raise ValueError(f"multiple evaluators found in directory: {self.path} ({paths})")

        if len(paths) == 0:
            raise ValueError(f"no evaluator found in directory: {self.path}")

        [path] = paths
        return path

    def _get_runner(self):
        assert os.path.isdir(self.path)

        evaluator_parameters = EvaluatorParameters(
            load_metadata(self.path).get("evaluator", {})
        )

        path = evaluator_parameters.path

        if path is None:
            path = self._find_evaluator()

        basepath, ext = os.path.splitext(path)

        runner_class = evaluator_runner_by_extension[ext]

        return runner_class(self.path, path, evaluator_parameters)

    def evaluate(self, files, seed=None):
        runner = self._get_runner()

        with ExitStack() as stack:
            if seed is None:
                seed = random.randrange(2 ** 31)

            env = {
                "TEMPORARY_DIRECTORY": stack.enter_context(TemporaryDirectory()),
                "TURINGARENA_SEED": str(seed),
                "TURINGARENA_LOG_LEVEL": logging.getLevelName(logging.root.getEffectiveLevel()),
            }

            command = stack.enter_context(runner.perform_run())

            evaluation = segi_subprocess(
                files,
                command,
                env=env,
                cwd=self.path,
            )

            yield from evaluation


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
