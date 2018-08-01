import os
import subprocess
import sys
from contextlib import ExitStack, contextmanager
from tempfile import TemporaryDirectory

from turingarena_impl.evaluation.evaluator import Evaluator
from turingarena_impl.logging import ok, info


def evaluate_cmd(files, evaluator="evaluator.py", raw=True):
    with ExitStack() as stack:
        output = sys.stdout

        if not raw:
            jq = stack.enter_context(subprocess.Popen(
                ["jq", "-j", "--unbuffered", ".payload"],
                stdin=subprocess.PIPE,
                universal_newlines=True,
            ))
            output = jq.stdin

        files = stack.enter_context(parse_files(files, ["source"]))
        ok("Submitted files")
        for name, path in files.items():
            info(f"{name}: {path}")

        evaluator = Evaluator.get_evaluator(evaluator)
        ok(f"Running evaluator: {evaluator}")
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