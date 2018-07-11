import subprocess
import json
import sys

from contextlib import ExitStack

from turingarena_impl.evaluation.cli import parse_files
from turingarena_impl.evaluation.evaluate import evaluate


def make_cmd():
    pass


def evaluate_cmd(json_args):
    evaluator = "python3 -u evaluator.py"

    if json_args["evaluator"]:
        evaluator = json_args["evaluator"]

    with ExitStack() as stack:
        if json_args["raw"]:
            output = sys.stdout
        else:
            jq = stack.enter_context(subprocess.Popen(
                ["jq", "-j", "--unbuffered", ".payload"],
                stdin=subprocess.PIPE,
                universal_newlines=True,
            ))
            output = jq.stdin

        files = stack.enter_context(parse_files(json_args["file"], ["source"]))

        for event in evaluate(files=files, evaluator_cmd=evaluator):
            print(event, file=output, flush=True)


def new_cli(args):
    json_args = json.loads(args[0])

    if json_args["command"] == "evaluate":
        evaluate_cmd(json_args)

    if json_args["command"] == "make":
        make_cmd()

