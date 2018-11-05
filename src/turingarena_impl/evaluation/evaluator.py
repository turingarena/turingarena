import logging
import os
import random
import subprocess
from abc import abstractmethod
from collections import namedtuple
from contextlib import ExitStack
from tempfile import TemporaryDirectory

from turingarena_impl.evaluation.segi import segi_subprocess


class Evaluator(namedtuple("Evaluator", ["cwd"])):
    def _compile(self, tmp_dir):
        pass

    @abstractmethod
    def _get_command(self, tmp_dir):
        pass

    def evaluate(self, files, seed=None):
        with ExitStack() as stack:
            tmp_dir = stack.enter_context(TemporaryDirectory())
            self._compile(tmp_dir)

            if seed is None:
                seed = random.randrange(2 ** 31)

            env = {
                "TEMPORARY_DIRECTORY": tmp_dir,
                "TURINGARENA_SEED": str(seed),
                "TURINGARENA_LOG_LEVEL": logging.getLevelName(logging.root.getEffectiveLevel()),
            }

            evaluation = segi_subprocess(
                files,
                self._get_command(tmp_dir),
                env=env,
                cwd=self.cwd,
            )

            for event in evaluation:
                yield event

    @staticmethod
    def get_evaluator(cwd):
        lookup = {
            "evaluator.py": PythonEvaluator,
            "evaluator.cpp": CppEvaluator,
            "evaluator.sh": BashEvaluator,
        }

        assert os.path.isdir(cwd)

        for name in os.listdir(cwd):
            try:
                evaluator_class = lookup[name]
                break
            except KeyError:
                pass
        else:
            raise ValueError(f"no evaluator found in directory: {cwd}")

        return evaluator_class(cwd)


class PythonEvaluator(Evaluator):
    def _get_command(self, tmp_dir):
        return [
            "python3",
            "-u",
            "evaluator.py",
        ]


class CppEvaluator(Evaluator):
    def _get_command(self, tmp_dir):
        return [os.path.join(tmp_dir, "evaluator")]

    def _compile(self, tmp_dir):
        cli = [
            "g++",
            "-std=c++14",
            "-Wall",
            "-o",
            os.path.join(tmp_dir, "evaluator"),
            "evaluator.cpp",
        ]

        subprocess.run(cli, cwd=self.cwd)


class BashEvaluator(Evaluator):
    def _get_command(self, tmp_dir):
        return ["bash", "evaluator.sh"]
