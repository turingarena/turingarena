"""TuringArena compute.

Usage:
  compute [options] [--dep <id>]... <cmd>

Options:
  --db=<db>  Location of the database
  --dep=<id>  Add a dependency
  <cmd>  The command to execute

"""

import docopt

from turingarena.compute import compute


def compute_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    return compute(
        command=args["<cmd>"],
        repo_path=args["--db"],
        deps=args["--dep"],
    )
