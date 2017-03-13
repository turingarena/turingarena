"""Task run.

Usage:
  taskrun <task-folder> <slot:submission>... [--maxproc=<maxproc>]
  taskrun (-h | --help)

Options:
  task-folder              Path to a task definition folder.
  slot:submission          Slot/submission pair (example: player1:sol/play.cpp)
  -h --help                Show this screen.
  --maxproc=<maxproc>      Max num of processes [default: 20].
"""

from docopt import docopt
import logging
import os
import pkg_resources
import shutil
import sys
import tempfile
import yaml

from taskwizard import supervisor


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

    with tempfile.TemporaryDirectory() as out_dir:
        os.mkdir(os.path.join(out_dir, "algorithms"))

        driver_path = os.path.join(out_dir, "driver")
        shutil.copytree(
            os.path.join(task_folder, "driver"),
            driver_path
        )
        os.system("g++ -g -o " + os.path.join(driver_path, "driver") +
                  " " + os.path.join(driver_path, "*.cpp"))

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
            os.system("g++ -g -o " + os.path.join(algorithm_path, "algorithm") +
                      " " + os.path.join(algorithm_path, "*.cpp"))

        os.mkdir(os.path.join(out_dir, "read_files"))

        supervisor.Supervisor(out_dir).run()
