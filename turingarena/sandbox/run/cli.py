"""TuringArena sandbox run.

Runs the given algorithm in a sandbox.

Usage:
  run [options] <algorithm>

Options:
  <algorithm>  Algorithm to run

"""
import docopt

from turingarena.sandbox.run import sandbox_run


def sandbox_run_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)
    sandbox_run(args["<algorithm>"])
