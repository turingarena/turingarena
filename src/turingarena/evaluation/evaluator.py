import logging
import os
import random
import subprocess
from contextlib import ExitStack
from functools import lru_cache
from tempfile import TemporaryDirectory

from turingarena.evallib.metadata import load_metadata
from turingarena.evaluation.runner import EvaluatorParameters
from turingarena.evaluation.runners import evaluator_runner_by_extension
from turingarena.evaluation.segi import segi_subprocess


class Evaluator:
    def __init__(self, evaluator_dir=None, evaluator_parameters=None, *, reset_env=False):
        if evaluator_dir is None:
            evaluator_dir = os.path.curdir

        if evaluator_parameters is None:
            evaluator_parameters = {}

        if not os.path.isdir(evaluator_dir):
            raise ValueError(f"not a directory: {evaluator_dir}")

        self.evaluator_dir = evaluator_dir
        self.parameter_overrides = evaluator_parameters
        self.reset_env = reset_env

    def _find_evaluators(self):
        filenames = os.listdir(self.evaluator_dir)
        for ext in evaluator_runner_by_extension:
            filename = f"evaluator{ext}"
            if filename in filenames:
                yield filename

    @property
    @lru_cache(None)
    def executable_path(self):
        path = self.evaluator_parameters.path
        if path is None:
            paths = list(self._find_evaluators())
            if len(paths) > 1:
                raise ValueError(f"multiple evaluators found in directory: {self.evaluator_dir} ({paths})")

            if len(paths) == 0:
                raise ValueError(f"no evaluator found in directory: {self.evaluator_dir}")
            [path] = paths
        return path

    @property
    def runner(self):
        basepath, ext = os.path.splitext(self.executable_path)
        runner_class = evaluator_runner_by_extension[ext]
        return runner_class(self.evaluator_dir, self.executable_path, self.evaluator_parameters)

    @property
    @lru_cache(None)
    def evaluator_parameters(self):
        return EvaluatorParameters({
            **load_metadata(self.evaluator_dir).get("evaluator", {}),
            **self.parameter_overrides,
        })

    def evaluate(self, files, seed=None, redirect_stderr=False):
        with ExitStack() as stack:
            if seed is None:
                seed = random.randrange(2 ** 31)

            env = {
                "TEMPORARY_DIRECTORY": stack.enter_context(TemporaryDirectory()),
                "TURINGARENA_SEED": str(seed),
                "TURINGARENA_LOG_LEVEL": logging.getLevelName(logging.root.getEffectiveLevel()),
            }

            command = stack.enter_context(self.runner.perform_run())

            popen_args = {}

            if redirect_stderr:
                popen_args["stderr"] = subprocess.STDOUT

            evaluation = segi_subprocess(
                files,
                command,
                env=env,
                reset_env=self.reset_env,
                cwd=self.evaluator_dir,
                **popen_args,
            )

            yield from evaluation
