import logging
import os
import sys
import subprocess

from contextlib import ExitStack
from tempfile import TemporaryDirectory
from docopt import docopt
from functools import wraps

from turingarena_impl.logging import init_logger
from turingarena_impl.tests.cli import test_cli

logger = logging.getLogger(__name__)

# TODO: legacy file. This file will be removed in the near future.


def docopt_cli(fun):
    @wraps(fun)
    def wrapped(argv=None, **kwargs):
        if argv is None:
            argv = sys.argv[1:]
        args = docopt(doc=fun.__doc__, argv=argv, options_first=True)
        fun(args, **kwargs)

    return wrapped


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
    init_logger(args["--log-level"])

    from turingarena_impl.api.serve import serve_cli

    commands = {
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

        argv2 = args["<args>"]
        commands[args["<cmd>"]](argv2)
