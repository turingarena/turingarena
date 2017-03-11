"""Task run.

Usage:
  taskrun <task-folder> <testcase-id> <slot:submission>... [--maxproc=<maxproc>]
  taskrun (-h | --help)

Options:
  task-folder              Path to a task definition folder.
  testcase-id              Testcase ID.
  slot:submission          Slot/submission pair (example: player1:sol/play.cpp)
  -h --help                Show this screen.
  --maxproc=<maxproc>      Max num of processes [default: 20].
"""

from docopt import docopt
import logging
import os
import shutil
import tempfile
import yaml


logger = logging.getLogger("taskrun")


def main():
    args = docopt(__doc__)
    print(args)

    if not os.path.isdir(args["<task-folder>"]):
        logger.critical("%s should be a folder", args["<task-folder>"])

    task_folder = args["<task-folder>"]
    slot_files = {}
    for slot in args["<slot:submission>"]:
        name, filename = slot.split(":", 2)
        slot_files[name] = filename

    task = yaml.safe_load(open(os.path.join(task_folder, "task.yaml")))

    out_dir = tempfile.mkdtemp()
    print("Dir: ", out_dir)

    os.mkdir(os.path.join(out_dir, "algorithms"))

    for slot_name, slot in task["slots"].items():
        algorithm_path = os.path.join(out_dir, "algorithms", slot_name)
        shutil.copytree(
            os.path.join(task_folder, "interfaces", slot["interface"]),
            algorithm_path
        )
        shutil.copy(
            slot_files[slot_name],
            os.path.join(algorithm_path, "algorithm.cpp")
        )
        os.system("g++ -o " + os.path.join(algorithm_path, "algorithm") +
                  " " + os.path.join(algorithm_path, "*.cpp"))
