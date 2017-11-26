"""TuringArena sandbox manager.

Usage:
  sandbox [options] <cmd> [<args>]...

Options:
  -h --help  Show this help.
"""
import docopt

from turingarena.sandbox.compile.cli import sandbox_compile_cli
from turingarena.sandbox.run.cli import sandbox_run_cli


def sandbox_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    commands = {
        "compile": sandbox_compile_cli,
        "run": sandbox_run_cli,
    }

    argv2 = args["<args>"]
    command = args["<cmd>"]

    commands[command](argv2)
