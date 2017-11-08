"""TuringArena evaluation.

Usage:
  evaluation [options] <cmd> [<args>...]

Options:
  --repo=<repo>  Location of the main repo

"""

import docopt

from turingarena.evaluation.compute_cli import evaluation_compute_cli
from turingarena.evaluation.entry_cli import evaluation_entry_cli


def evaluation_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    commands = {
        "entry": evaluation_entry_cli,
        "compute": evaluation_compute_cli,
    }
    argv2 = args["<args>"]
    return commands[args["<cmd>"]](argv=argv2, repo_path=args["--repo"])
