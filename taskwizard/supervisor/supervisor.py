"""Task run.

Usage:
  taskrun <task-folder> <testcase-id> <slot:submission>... [--maxproc=<maxproc>]
  taskrun (-h | --help)

Options:
  task-folder          Path to a task definition folder.
  testcase-id          Testcase ID.
  slot:submission      Slot/submission pair (example: player1:sol/play.cpp)
  -h --help            Show this screen.
  --maxproc=<maxproc>  Max num of processes [default: 20].
"""

import logging
import os
import shutil
import tempfile

from docopt import docopt


logger = logging.getLogger("taskrun")


def main():
    args = docopt(__doc__)
    print(args)

    if not os.path.isdir(args["<task-folder>"]):
        logger.critical("%s should be a folder", args["<task-folder>"])

    with tempfile.TemporaryDirectory() as tmpdirname:
        shutil.copytree(args["<task-folder>"], tmpdirname)

    pass
