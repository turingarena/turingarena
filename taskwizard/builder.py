"""Task Builder.

Usage:
  taskmake (prepare|clean) [ -C <dir> ]
  taskmake -h | --help

Options:
  prepare            Prepares the task
  -C --chdir=<dir>   Change the current directory to <dir>
  -h --help          Show this screen.
"""

from docopt import docopt
import os
import shutil

from taskwizard.preparer import ProblemPreparer


def main():
    args = docopt(__doc__)

    chdir = args["--chdir"]
    if chdir:
        os.chdir(chdir)

    os.makedirs("build", exist_ok=True)

    if args["clean"]:
        shutil.rmtree("build")

    if args["prepare"]:
        prepared_dir = os.path.join("build", "prepared")
        shutil.rmtree(prepared_dir, ignore_errors=True)
        ProblemPreparer(".", prepared_dir).prepare()
