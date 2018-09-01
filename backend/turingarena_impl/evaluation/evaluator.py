import logging
import os
import subprocess
from contextlib import ExitStack
from tempfile import TemporaryDirectory

from turingarena_impl.evaluation.segi import segi_subprocess
from turingarena_impl.evaluation.turingarena_tools import run_metaservers


class Evaluator:
    def __init__(self, filename, cwd):
        self.filename = filename
        self.command = filename
        self.cwd = cwd

    def evaluate(self, files):
        with ExitStack() as stack:
            env = stack.enter_context(run_metaservers())
            tmp_dir = stack.enter_context(TemporaryDirectory())
            self.compile(tmp_dir)

            env = {
                **env,
                "TEMPORARY_DIRECTORY": tmp_dir,
            }

            evaluation = segi_subprocess(
                files,
                self.command,
                shell=True,
                env=env,
                cwd=self.cwd,
            )

            for event in evaluation:
                yield event

    def compile(self, tmp_dir):
        pass

    @staticmethod
    def get_evaluator(filename, cwd):
        evaluator_class = Evaluator

        path = os.path.join(cwd, filename)
        logging.debug(f"Evaluator {filename} in work dir {cwd}")
        if os.path.exists(path):
            extension = os.path.splitext(path)[1]
            logging.debug(f"Evaluator {filename} has extension {extension}")
            try:
                evaluator_class = {
                    ".py": PythonEvaluator,
                    ".cpp": CppEvaluator,
                }[extension]
            except KeyError:
                pass

        return evaluator_class(filename, cwd=cwd)

    def __str__(self):
        return "generic evaluator"


class PythonEvaluator(Evaluator):
    def compile(self, tmp_dir):
        self.command = f"python3 -u {self.filename}"

    def __str__(self):
        return "python evaluator"


class CppEvaluator(Evaluator):
    def compile(self, tmp_dir):
        self.command = os.path.join(tmp_dir, "evaluator")
        cli = [
            "g++",
            "-std=c++14",
            "-Wall",
            "-o",
            self.command,
            self.filename,
        ]

        subprocess.call(cli)

    def __str__(self):
        return "C++ evaluator"
