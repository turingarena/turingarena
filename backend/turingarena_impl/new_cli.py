import subprocess
import logging
import json
import sys
import os

from contextlib import ExitStack, contextmanager
from tempfile import TemporaryDirectory
from termcolor import colored


from turingarena_impl.evaluation.cli import parse_files
from turingarena_impl.evaluation.evaluate import evaluate
from turingarena_impl.driver.interface.interface import InterfaceDefinition
from turingarena_impl.driver.language import Language
from turingarena_impl.driver.interface.metadata import generate_interface_metadata


logger = logging.getLogger(__name__)
git_env = {}

def error(string):
    print(colored("==> ERROR:", "red", attrs=["bold"]), string)


def warning(string):
    print(colored("==> WARNING:", "yellow", attrs=["bold"]), string)


def ok(string):
    print(colored("==>", "green", attrs=["bold"]), string)


def info(string):
    print(colored("  ->", "blue", attrs=["bold"]), string)


@contextmanager
def setup_git_environment(local, git_dir):
    global git_env

    ok("Setting up git")
    with ExitStack() as stack:
        git_temp_dir = stack.enter_context(TemporaryDirectory())
        info(f"Created temporary git working dir {git_temp_dir}")
        if not local:
            git_dir = "/run/turingarena/db.git"
        info(f"Using git repository at {git_dir}")
        git_env = {
            "GIT_DIR": git_dir,
            "GIT_WORK_TREE": git_temp_dir,
        }
        os.chdir(git_temp_dir)
        yield


def git_fetch_repositories(repositories):
    for repository in repositories:
        # TODO: add a way to specify branch and depth
        ok(f"Fetching git repository {repository}")
        subprocess.call(["git", "fetch", "--recurse-submodules=yes", repository], env=git_env)


def git_import_trees(tree_ids):
    for tree_id in tree_ids:
        ok(f"Importing git tree id {tree_id}")
        subprocess.call(["git", "read-tree", tree_id], env=git_env)
        subprocess.call(["git", "checkout-index", "--all"], env=git_env)


def receive_current_directory(current_dir, tree_id):
    ok("Retriving current directory from git")

    git_import_trees([tree_id])

    if current_dir:
        os.chdir(current_dir)


def commit_work(directory):
    ok(f"Committing generated directory {directory}")

    subprocess.call(["git", "add", "-A", directory], env=git_env)
    tree_id = subprocess.check_output(["git", "write-tree"], env=git_env).strip().decode("ascii")
    info(f"Output written with tree-id {tree_id}")
    return tree_id

@contextmanager
def generate(filename):
    info(f"Generating {filename}... ")
    with open(filename, "w") as file:
        try:
            yield file
        except:
            error(f"Exception during {filename} generation")


def make_skeleton(out_dir, interface, language):
    with generate(f"{out_dir}/skeleton{language.extension}") as out:
            language.skeleton_generator().generate_to_file(interface, out)


def make_template(out_dir, interface, language):
    with generate(f"{out_dir}/template{language.extension}") as out:
        language.template_generator().generate_to_file(interface, out)


def make_metadata(out_dir, interface):
    with generate(f"{out_dir}/metadata.json") as out:
        json.dump(generate_interface_metadata(interface), out, indent=4)


def make(directory, what, languages):
    out_dir = os.path.join(directory, "__turingarena_make_output__")
    os.makedirs(out_dir, exist_ok=True)

    ok(f"Entering directory {directory}")

    interface_file = os.path.join(directory, "interface.txt")

    with open(interface_file) as f:
        interface_text = f.read()

    try:
        interface = InterfaceDefinition.compile(interface_text)
    except:
        error(f"There is an error in {interface_file}")
        return

    for message in interface.validate():
        warning(f"WARNING: {message}")

    for language in languages:
        language_dir = os.path.join(out_dir, language.name)
        os.makedirs(language_dir, exist_ok=True)

        if "skeleton" in what:
            make_skeleton(out_dir=language_dir, interface=interface, language=language)
        if "template" in what:
            make_template(out_dir=language_dir, interface=interface, language=language)

    if "metadata" in what:
        make_metadata(out_dir=out_dir, interface=interface)


def make_cmd(args):
    what = args["what"]

    if what == "all":
        what = ["skeleton", "template", "metadata"]
    else:
        what = [what]

    languages = []
    if args["language"]:
        for language in args["language"]:
            try:
                languages.append(Language.from_name(language))
            except ValueError:
                error(f"Language {language} not supported")
    else:
        languages = Language.languages()

    ok(f"Searching for problems in {os.getcwd()}")
    for subdir, dir, files in os.walk(os.getcwd()):
        if "interface.txt" in files:
            make(directory=subdir, what=what, languages=languages)

    commit_work(os.getcwd())

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

        ok(f"Parsing submitted files")
        files = stack.enter_context(parse_files(json_args["file"], ["source"]))
        for name, path in files.items():
            info(f"{name}: {path}")

        ok(f"Running evaluator command {evaluator}")
        for event in evaluate(files=files, evaluator_cmd=evaluator):
            print(event, file=output, flush=True)


def new_cli(args):
    args = json.loads(args[0])

    with setup_git_environment(local=args["local"], git_dir=args["git_dir"]):

        receive_current_directory(args["current_dir"], args["tree_id"])

        if args["repository"]:
            git_fetch_repositories(args["repository"])

        if args["tree"]:
            git_import_trees(args["tree"])

        if args["command"] == "evaluate":
            evaluate_cmd(args)

        if args["command"] == "make":
            make_cmd(args)

