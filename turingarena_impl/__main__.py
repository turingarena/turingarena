import logging
import os
from contextlib import ExitStack
from tempfile import TemporaryDirectory

from future.moves import subprocess

from turingarena_impl.cli import docopt_cli, init_logger
from turingarena_impl.interface.cli import generate_template_cli, generate_skeleton_cli, validate_interface_cli
from turingarena_impl.problem.cli import evaluate_cli
from turingarena_impl.tests.cli import test_cli
from turingarena_impl.web.serve import serve_cli

logger = logging.getLogger(__name__)


@docopt_cli
def server_cli(args):
    """TuringArena command line interface.

    Usage:
      turingarena [options] <cmd> [<args>]...
      turingarena --help-commands

    Options:
      --log-level=<level>  Set logging level.
      --help-commands  Show list of available commands.
    """
    init_logger(args)

    commands = {
        "evaluate": evaluate_cli,
        "template": generate_template_cli,
        "skeleton": generate_skeleton_cli,
        "validate": validate_interface_cli,
        "serve": serve_cli,
        "test": test_cli,
    }

    if args["--help-commands"]:
        print("Avaliable commands:")
        print()
        for c, cli in commands.items():
            doc = cli.__doc__.splitlines(keepends=False)[0]
            print(f"{c:20} {doc}")
        print()
        print("For further help: turingarena <command> -h")
        return

    tree_id = os.environ.get("TURINGARENA_TREE_ID", None)
    with ExitStack() as stack:
        if tree_id is not None:
            temp_dir = stack.enter_context(TemporaryDirectory())
            logger.info(f"unpacking tree {tree_id} in {temp_dir}")
            os.chdir(temp_dir)
            git_env = {
                "GIT_DIR": "/run/turingarena/db.git",
                "GIT_WORK_TREE": ".",
            }
            subprocess.run(["git", "read-tree", tree_id], env=git_env)
            subprocess.run(["git", "checkout-index"], env=git_env)

        argv2 = args["<args>"]
        commands[args["<cmd>"]](argv2)


if __name__ == '__main__':
    server_cli()
