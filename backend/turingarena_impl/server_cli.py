import subprocess
import logging
import json
import sys
import os

from contextlib import ExitStack, contextmanager
from tempfile import TemporaryDirectory

from turingarena_impl.evaluation.cli import parse_files
from turingarena_impl.evaluation.evaluate import Evaluator
from turingarena_impl.driver.interface.interface import InterfaceDefinition
from turingarena_impl.driver.language import Language
from turingarena_impl.driver.interface.metadata import generate_interface_metadata
from turingarena_impl.logging import error, warning, ok, info, init_logger


logger = logging.getLogger(__name__)
git_env = {}


@contextmanager
def setup_git_environment(local, git_dir):
    global git_env

    logger.info("Setting up git")
    with ExitStack() as stack:
        git_temp_dir = stack.enter_context(TemporaryDirectory())
        logger.info(f"Created temporary git working dir {git_temp_dir}")
        if not local:
            git_dir = "/run/turingarena/db.git"
        logger.info(f"Using git repository at {git_dir}")
        author_name = "TuringArena"
        author_email = "contact@turingarena.org"
        git_env = {
            "GIT_DIR": git_dir,
            "GIT_WORK_TREE": git_temp_dir,
            "GIT_AUTHOR_NAME": author_name,
            "GIT_AUTHOR_EMAIL": author_email,
            "GIT_COMMITTER_NAME": author_name,
            "GIT_COMMITTER_EMAIL": author_email,

        }
        os.chdir(git_temp_dir)
        yield


def git_fetch_repositories(repositories):
    for repository in repositories:
        # TODO: add a way to specify branch and depth
        logger.info(f"Fetching git repository {repository}")
        subprocess.call(["git", "fetch", "--recurse-submodules=yes", repository], env=git_env)


def git_import_trees(tree_ids):
    for tree_id in tree_ids:
        logger.info(f"Importing git tree id {tree_id}")
        subprocess.call(["git", "read-tree", tree_id], env=git_env)
        subprocess.call(["git", "checkout-index", "--all"], env=git_env)


def receive_current_directory(current_dir, tree_id):
    logger.info("Retriving current directory from git")

    git_import_trees([tree_id])

    if current_dir:
        os.chdir(current_dir)


def add_directory(directory):
    logger.info(f"Add directory {directory} to be committed")
    subprocess.call(["git", "add", "-A", directory], env=git_env)


def commit_work():
    logger.info("Committing work")

    tree_id = subprocess.check_output(["git", "write-tree"], env=git_env).strip().decode("ascii")
    logger.info(f"Output written with tree-id {tree_id}")

    commit_id = subprocess.check_output(["git", "commit-tree", tree_id, "-m", "Make output"], env=git_env).strip().decode("ascii")
    logger.info(f"Created commit with commit-id {commit_id}")

    return tree_id, commit_id


@contextmanager
def generate(dir, filename):
    if dir is None:
        ok(f"Printing {filename}")
        yield sys.stdout
    else:
        file = os.path.join(dir, filename)
        info(f"Generating {os.path.relpath(file, git_env['GIT_WORK_TREE'])}")
        with open(file, "w") as f:
            try:
                yield f
            except:
                error(f"Exception during {filename} generation")


def make_skeleton(out_dir, interface, language):
    with generate(out_dir, f"skeleton{language.extension}") as out:
            language.skeleton_generator().generate_to_file(interface, out)


def make_template(out_dir, interface, language):
    with generate(out_dir, f"template{language.extension}") as out:
        language.template_generator().generate_to_file(interface, out)


def make_metadata(out_dir, interface):
    with generate(out_dir, f"metadata.json") as out:
        json.dump(generate_interface_metadata(interface), out, indent=4)


def make(directory, what, languages, print):
    out_dir = None
    if not print:
        out_dir = os.path.join(directory, "__turingarena_make_output__")
        os.makedirs(out_dir, exist_ok=True)

    ok(f"Entering directory {os.path.relpath(directory, git_env['GIT_WORK_TREE'])}")

    interface_file = os.path.join(directory, "interface.txt")

    with open(interface_file) as f:
        interface_text = f.read()

    logger.info("Compiling interface")
    try:
        interface = InterfaceDefinition.compile(interface_text)
    except:
        error(f"There is an error in {interface_file}")
        return

    for message in interface.validate():
        warning(f"{message}")

    for language in languages:
        language_dir = None
        if out_dir:
            language_dir = os.path.join(out_dir, language.name)
            os.makedirs(language_dir, exist_ok=True)

        if "skeleton" in what:
            make_skeleton(out_dir=language_dir, interface=interface, language=language)
        if "template" in what:
            make_template(out_dir=language_dir, interface=interface, language=language)

    if "metadata" in what:
        make_metadata(out_dir=out_dir, interface=interface)

    if not print:
        add_directory(out_dir)


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

    base_dir = os.getcwd()
    ok(f"Searching for problems in {os.path.relpath(base_dir, git_env['GIT_WORK_TREE'])}")
    for subdir, dir, files in os.walk(base_dir):
        if "interface.txt" in files:
            make(directory=subdir, what=what, languages=languages, print=args["print"])

    if not args["print"]:
        tree_id, commit_id = commit_work()
        result = dict(tree_id=tree_id, commit_id=commit_id)
        logger.info(f"Writing result to file {args['result_file']}")
        with open(args["result_file"], "w") as f:
            print(json.dumps(result), file=f)


def evaluate_cmd(json_args):
    evaluator = "evaluator.py"

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

        evaluator = Evaluator.get_evaluator(evaluator)
        ok(f"Running evaluator: {evaluator}")
        for event in evaluator.evaluate(files=files):
            print(event, file=output, flush=True)


def info_languages():
    print("Supported languages\n")
    print("Name\tExtension\tSupported for evaluator")
    print("----\t---------\t-----------------------")
    for language in Language.languages():
        print(f"{language.name}\t{language.extension}\t\t{'yes' if language.supported_for_evaluator else 'no'}")


def info_cmd(args):
    what = args["what"]

    if what == "languages":
        info_languages()


def main(args):
    args = json.loads(args[0])

    init_logger(args["log_level"])

    with setup_git_environment(local=args["local"], git_dir=args["git_dir"]):

        if args["send_current_dir"]:
            receive_current_directory(args["current_dir"], args["tree_id"])

        if args["repository"]:
            git_fetch_repositories(args["repository"])

        if args["tree"]:
            git_import_trees(args["tree"])

        if args["command"] == "evaluate":
            evaluate_cmd(args)

        if args["command"] == "make":
            make_cmd(args)

        if args["command"] == "info":
            info_cmd(args)


if __name__ == "__main__":
    main(sys.argv[1:])
