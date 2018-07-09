import json
import sys

from contextlib import ExitStack

from turingarena_impl.evaluation.cli import parse_files
from turingarena_impl.evaluation.evaluate import evaluate


def make():
    pass


def evaluate_cmd(json_args):
    evaluator = "python3 -u evaluator.py"

    with ExitStack() as stack:
        files = stack.enter_context(parse_files(json_args["submitted_files"], ["source"]))

        for event in evaluate(files=files, evaluator_cmd=evaluator):
            print(event, file=sys.stdout, flush=True)


def new_cli(args):
    json_args = json.loads(args[0])

    if json_args["command"] == "evaluate":
        evaluate_cmd(json_args)

    if json_args["command"] == "make":
        make()

