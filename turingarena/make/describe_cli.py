"""TuringArena task describe CLI.

Usage:
  describe
"""

import docopt


def make_describe_cli(*, plan, argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)
    print(plan)
