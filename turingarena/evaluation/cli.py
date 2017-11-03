"""TuringArena evaluation.

Usage:
  evaluation [options]
"""

import docopt

from turingarena.evaluation import Task


def evaluation_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)
