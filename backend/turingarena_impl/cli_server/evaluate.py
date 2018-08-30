import logging
import os
import subprocess
import sys
from contextlib import ExitStack, contextmanager
from tempfile import TemporaryDirectory

from turingarena_common.commands import EvaluateCommandParameters
from turingarena_impl.cli_server.pack import enter_working_directory
from turingarena_impl.evaluation.evaluator import Evaluator


def evaluate_cmd(parameters: EvaluateCommandParameters):
    with ExitStack() as stack:
        stack.enter_context(enter_working_directory(parameters.working_directory))

        output = sys.stdout

        if not parameters.raw_output:
            jq = stack.enter_context(subprocess.Popen(
                ["jq", "-j", "--unbuffered", ".payload"],
                stdin=subprocess.PIPE,
                universal_newlines=True,
            ))
            output = jq.stdin

        files = stack.enter_context(parse_files(parameters.file, ["source"]))
        logging.info("Submitted files")
        for name, path in files.items():
            logging.info(f"{name}: {path}")

        evaluator = Evaluator.get_evaluator(parameters.evaluator)
        logging.info(f"Running evaluator: {evaluator}")
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