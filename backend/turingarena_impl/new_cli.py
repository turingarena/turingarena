import subprocess
import json
import sys

from contextlib import ExitStack

from turingarena_impl.evaluation.cli import parse_files
from turingarena_impl.evaluation.evaluate import evaluate


def git_fetch_repositories(repositories):
    for repository in repositories:
        # TODO: add a way to specify branch and depth
        subprocess.call(["git", "fetch", "-recurse-submodules=yes", repository])


def git_import_trees(tree_ids):
    for id in tree_ids:
        subprocess.call(["git", "read-tree", id])
        subprocess.call(["git", "checkout", "--all"])


def make_cmd(args):
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
    args = json.loads(args[0])

    if args["repository"]:
        git_fetch_repositories(args["repository"])

    if args["tree"]:
        git_import_trees(args["tree"])

    if args["command"] == "evaluate":
        evaluate_cmd(args)

    if args["command"] == "make":
        make_cmd(args)

