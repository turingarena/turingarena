"""TuringArena compute.

Usage:
  compute [options] [--parent <id>]... [--] <cmd>...

Options:
  --db=<db>  Location of the database
  --parent=<id>  Add a parent
  <cmd>  The command to execute

"""

import docopt

from turingarena.compute import compute


def compute_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    return compute(
        command=" ".join(args["<cmd>"]),
        repo_path=args["--db"],
        parents=args["--parent"],
    )
