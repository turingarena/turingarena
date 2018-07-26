import os
import subprocess
import sys
from contextlib import contextmanager, ExitStack
from tempfile import TemporaryDirectory

from turingarena_impl.legacy_cli import docopt_cli
from turingarena_impl.evaluation.evaluate import Evaluator


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
        -e --evaluator=<id>  Evaluator [default: evaluator.py]
        -r --raw  Output events in JSON Lines format.
    """

    with ExitStack() as stack:
        if args["--raw"]:
            output = sys.stdout
        else:
            jq = stack.enter_context(subprocess.Popen(
                ["jq", "-j", "--unbuffered", ".payload"],
                stdin=subprocess.PIPE,
                universal_newlines=True,
            ))
            output = jq.stdin

        files = stack.enter_context(parse_files(args["<files>"], ["source"]))

        for event in Evaluator.get_evaluator(args["--evaluator"]).evaluate(files=files):
            print(event, file=output, flush=True)
