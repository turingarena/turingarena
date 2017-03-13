"""Task Builder.

Usage:
  taskmake init [<name>] [ -C <dir> ]
  taskmake -h | --help

Options:
  init               Initializes new task in the current directory
  <name>             Task name [default: unnamed_task]
  -C --chdir=<dir>   Change the current directory to <dir>
  -h --help          Show this screen.
"""

from docopt import docopt
from jinja2 import Environment, PackageLoader
import os


def main():
    args = docopt(__doc__)

    chdir = args["--chdir"]
    if chdir:
        os.chdir(chdir)

    if args["init"]:
        raise NotImplementedError
