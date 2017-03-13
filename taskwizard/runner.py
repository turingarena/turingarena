"""Task run.

Usage:
  taskrun [<slot:submission>...] [-i <prepared-dir>] [-e <evaluation>] [-p <phase>] [--maxproc=<maxproc>]
  taskrun (-h | --help)

Options:
  -i --input=<prepared-dir>     Path to the problem prepared folder [default: ./build/prepared/].
  -e --evaluation=<evaluation>  Which evaluation to apply [default: main]
  -p --phase=<phase>            Which phase to run [default: evaluate]
  slot:submission               Slot/submission pair (example: player1:sol/play.cpp)
  -h --help                     Show this screen.
  --maxproc=<maxproc>           Max num of processes [default: 20].
"""

from cmath import phase
from docopt import docopt
import logging
import os
import pkg_resources
import shutil
import sys
import tempfile
import yaml

from taskwizard import supervisor


class PhaseExecution:

    def __init__(self, phase, execution_dir):
        self.phase = phase
        self.execution_dir = execution_dir
        self.driver_dir = os.path.join(self.execution_dir, "driver")

    def execute(self, slots):
        os.mkdir(os.path.join(self.execution_dir, "algorithms"))
        shutil.copytree(
            self.phase.driver_dir,
            self.driver_dir
        )
        os.system("g++ -g -o " + os.path.join(self.driver_dir, "driver") +
                  " " + os.path.join(self.driver_dir, "*.cpp"))

        for slot_name, slot in self.phase.algorithm_slots.items():
            algorithm_path = os.path.join(self.execution_dir, "algorithms", slot_name)
            shutil.copytree(
                os.path.join(self.phase.prepared_dir, "interfaces", slot["interface"]),
                algorithm_path
            )
            shutil.copy(
                slots[slot_name],
                os.path.join(algorithm_path, "algorithm.cpp")
            )
            os.system("g++ -g -o " + os.path.join(algorithm_path, "algorithm") +
                      " " + os.path.join(algorithm_path, "*.cpp"))

        os.mkdir(os.path.join(self.execution_dir, "read_files"))

        supervisor.Supervisor(self.execution_dir).run()


class Phase:

    def __init__(self, prepared_dir, evaluation_name, phase_name):
        self.prepared_dir = prepared_dir
        self.evaluation_name = evaluation_name
        self.phase_name = phase_name

        self.evaluation_dir = os.path.join(prepared_dir, "evaluations", evaluation_name)
        self.evaluation_conf_path = os.path.join(self.evaluation_dir, "evaluation.yaml")

    def load_evaluation_conf(self):
        self.evaluation_conf = yaml.safe_load(open(self.evaluation_conf_path))

        self.phase_conf = self.evaluation_conf["phases"][self.phase_name]

        self.algorithm_slots = self.phase_conf["slots"]
        self.driver_name = self.phase_conf["driver"]

        self.driver_dir = os.path.join(self.prepared_dir, "drivers", self.driver_name)

    def run(self, slots):
        self.load_evaluation_conf()

        with tempfile.TemporaryDirectory() as execution_dir:
            PhaseExecution(self, execution_dir).execute(slots)


def main():
    args = docopt(__doc__)

    slots = {}
    for slot in args["<slot:submission>"]:
        name, filename = slot.split(":", 2)
        slots[name] = filename

    Phase(args["--input"], args["--evaluation"], args["--phase"]).run(slots)

