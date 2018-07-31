import os
import subprocess
import sys
import logging

from contextlib import ExitStack, contextmanager
from tempfile import TemporaryDirectory

from turingarena_impl.evaluation.evaluator import Evaluator

logger = logging.Logger(__name__)


def evaluate_cmd(args):
    evaluator = "evaluator.py"

    if args["evaluator"]:
        evaluator = args["evaluator"]

    with ExitStack() as stack:
        if args["raw"]:
            output = sys.stdout
        else:
            jq = stack.enter_context(subprocess.Popen(
                ["jq", "-j", "--unbuffered", ".payload"],
                stdin=subprocess.PIPE,
                universal_newlines=True,
            ))
            output = jq.stdin

        logger.info(f"Parsing submitted files")
        files = stack.enter_context(parse_files(args["file"], ["source"]))
        for name, path in files.items():
            logger.info(f"{name}: {path}")

        evaluator = Evaluator.get_evaluator(evaluator)
        logger.info(f"Running evaluator: {evaluator}")
        for event in evaluator.evaluate(files=files):
            print(event, file=output, flush=True)


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