"""Naval Fate.

Usage:
  taskrun <task-folder> <submission> [--maxproc=<maxproc>]
  taskrun (-h | --help)

Options:
  -h --help            Show this screen.
  --maxproc=<maxproc>  Max num of processes [default: 20].
"""

import logging
import os

from docopt import docopt


logger = logging.getLogger("taskrun")


def main():
    args = docopt(__doc__)

    if not os.path.isdir(args["<task-folder>"]):
        logger.critical("%s should be a folder", args["<task-folder>"])
