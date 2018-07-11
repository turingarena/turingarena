import subprocess
import logging
import json
import sys
import os

from contextlib import ExitStack
from tempfile import TemporaryDirectory

from turingarena_impl.evaluation.cli import parse_files
from turingarena_impl.evaluation.evaluate import evaluate
from turingarena_impl.driver.interface.interface import InterfaceDefinition
from turingarena_impl.driver.language import Language


logger = logging.getLogger(__name__)


def git_fetch_repositories(repositories):
    for repository in repositories:
        # TODO: add a way to specify branch and depth
        subprocess.call(["git", "fetch", "-recurse-submodules=yes", repository])


def git_import_trees(tree_ids):
    for id in tree_ids:
        subprocess.call(["git", "read-tree", id])
        subprocess.call(["git", "checkout", "--all"])


def receive_current_directory():
    tree_id = os.environ.get("TURINGARENA_TREE_ID", None)
    current_dir = os.environ.get("TURINGARENA_CURRENT_DIR", None)

    with ExitStack() as stack:
        if tree_id is not None:
            temp_dir = stack.enter_context(TemporaryDirectory())
            logger.info(f"unpacking tree {tree_id} in {temp_dir}")
            git_env = {
                "GIT_DIR": "/run/turingarena/db.git",
                "GIT_WORK_TREE": temp_dir,
            }
            subprocess.run(["git", "read-tree", tree_id], env=git_env)
            subprocess.run(["git", "checkout-index", "--all"], env=git_env)
            os.chdir(temp_dir)
            if current_dir is not None:
                os.chdir(current_dir)


def make_skeletons(outdir, interface, languages):
    os.makedirs(os.path.join(outdir, "skeletons"), exist_ok=True)
    for language in languages:
        language = Language.from_name(language)
        with open(f"{outdir}/skeletons/skeleton{language.extension}", "w") as out:
            language.skeleton_generator().generate_to_file(interface, out)


def make_templates(outdir, interface, languages):
    os.makedirs(os.path.join(outdir, "templates"), exist_ok=True)
    for language in languages:
        language = Language.from_name(language)
        with open(f"{outdir}/templates/template{language.extension}", "w") as out:
            language.template_generator().generate_to_file(interface, out)


def make_cmd(args):
    out_dir = os.path.join(os.getcwd(), "__turingarena_make_output__")
    os.makedirs(out_dir, exist_ok=True)

    logger.info(f"saving generate file in {out_dir}")

    interface_file = "interface.txt"

    with open(interface_file) as f:
        interface_text = f.read()
    interface = InterfaceDefinition.compile(interface_text)

    make_skeletons(outdir=out_dir, interface=interface, languages=["c++", "python"])
    make_templates(outdir=out_dir, interface=interface, languages=["c++", "python"])
    #make_metadata()


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

    if args["send_current_dir"]:
        receive_current_directory()

    if args["repository"]:
        git_fetch_repositories(args["repository"])

    if args["tree"]:
        git_import_trees(args["tree"])

    if args["command"] == "evaluate":
        evaluate_cmd(args)

    if args["command"] == "make":
        make_cmd(args)

