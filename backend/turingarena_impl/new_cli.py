import subprocess
import logging
import json
import sys
import os

from contextlib import ExitStack, contextmanager
from tempfile import TemporaryDirectory

from turingarena_impl.evaluation.cli import parse_files
from turingarena_impl.evaluation.evaluate import evaluate
from turingarena_impl.driver.interface.interface import InterfaceDefinition
from turingarena_impl.driver.language import Language
from turingarena_impl.driver.interface.metadata import generate_interface_metadata


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


@contextmanager
def generate(filename):
    print(f"Generating {filename}")
    with open(filename, "w") as file:
        yield file


def make_skeletons(out_dir, interface, language):
    with generate(f"{out_dir}/skeleton{language.extension}") as out:
        language.skeleton_generator().generate_to_file(interface, out)


def make_templates(out_dir, interface, language):
    with generate(f"{out_dir}/template{language.extension}") as out:
        language.template_generator().generate_to_file(interface, out)


def make_metadata(out_dir, interface):
    with generate(f"{out_dir}/metadata.json") as out:
        json.dump(generate_interface_metadata(interface), out, indent=4)


def make(directory):
    out_dir = os.path.join(directory, "__turingarena_make_output__")
    os.makedirs(out_dir, exist_ok=True)

    print(f"Entering directory {directory}")

    interface_file = os.path.join(directory, "interface.txt")

    with open(interface_file) as f:
        interface_text = f.read()

    try:
        interface = InterfaceDefinition.compile(interface_text)
    except:
        print(f"There is an error in {interface_file}")
        return

    for message in interface.validate():
        print(f"Warning: {message}")

    for language in Language.languages():
        try:
            language_dir = os.path.join(out_dir, language.name)
            os.makedirs(language_dir, exist_ok=True)
            make_skeletons(out_dir=language_dir, interface=interface, language=language)
            make_templates(out_dir=language_dir, interface=interface, language=language)
        except:
            pass
    make_metadata(out_dir=out_dir, interface=interface)


def make_cmd(args):
    for subdir, dir, files in os.walk(os.getcwd()):
        if "interface.txt" in files:
            make(subdir)


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

