import os
import subprocess

from contextlib import ExitStack, contextmanager
from tempfile import TemporaryDirectory

from turingarena_impl.evaluation.segi import segi_subprocess
from turingarena_impl.evaluation.turingarena_tools import run_metaservers


@contextmanager
def parse_files(files, default_fields):
    default_fields = iter(default_fields)
    with TemporaryDirectory() as temp_dir:
        yield dict(
            parse_file(arg, temp_dir, default_fields)
            for arg in files
        )


def parse_file(file, temp_dir, default_fields):
    if ":" in file:
        name, path = file.split(":", 1)
    elif "=" in file:
        name, value = file.split("=", 1)
        path = os.path.join(temp_dir, name + ".txt")
        with open(path, "x") as f:
            f.write(value)
    else:
        name = next(default_fields)
        path = file
    return name, path


class Evaluator:
    def __init__(self, filename):
        self.filename = filename
        self.command = filename

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
            )

            for event in evaluation:
                yield event

    def compile(self, tmp_dir):
        pass

    @staticmethod
    def get_evaluator(filename):
        extension = os.path.splitext(filename)[1]

        try:
            return {
                ".py": PythonEvaluator,
                ".cpp": CppEvaluator,
            }[extension](filename)
        except KeyError:
            return Evaluator(filename)

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

