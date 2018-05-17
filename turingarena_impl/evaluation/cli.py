import os
from contextlib import contextmanager
from tempfile import TemporaryDirectory

from turingarena_impl.cli import docopt_cli
from turingarena_impl.evaluation.python import PythonEvaluator


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


@docopt_cli
def evaluate_cli(args):
    """Evaluates a submission.

    Usage:
        evaluate [options] <files> ...

    Options:
        -e --evaluator=<id>  Evaluator [default: ./evaluate.py]
    """

    with parse_files(args["<files>"], ["source"]) as files:
        evaluation = PythonEvaluator(args["--evaluator"]).evaluate(files)

        for event in evaluation:
            print(event)
