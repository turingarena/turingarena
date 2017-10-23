"""TuringArena sandbox manager.

Usage:
  sandbox [options] (compile|run) [<args>]...

Options:
  -h --help  Show this help.
"""
import docopt

from turingarena.sandbox.compile.cli import sandbox_compile_cli
from turingarena.sandbox.run.cli import sandbox_run_cli


def sandbox_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    argv2 = args["<args>"]
    if args["compile"]: return sandbox_compile_cli(argv2)
    if args["run"]: return sandbox_run_cli(argv2)
