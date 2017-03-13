"""Task run.

Usage:
  taskrun <testcase> [<slot:submission>...] [-i <prepared-dir>] [-o <output_dir>] [-p <phase>] [--maxproc=<maxproc>]
  taskrun (-h | --help)

Options:
  <testcase>                    Which testcase to run [default: main]
  -i --input=<prepared-dir>     Path to the problem prepared folder [default: ./build/prepared/].
  -o --output=<output-dir>      Path to the folder where to put evaluation results
  -p --phase=<phase>            Which phase to run [default: evaluate]
  slot:submission               Slot/submission pair (example: player1:sol/play.cpp)
  -h --help                     Show this screen.
  --maxproc=<maxproc>           Max num of processes [default: 20].
"""

from cmath import phase
from datetime import datetime
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

    def execute(self, slots, output_dir):
        os.mkdir(os.path.join(self.execution_dir, "algorithms"))
        shutil.copytree(
            self.phase.driver_dir,
            self.driver_dir
        )
        os.system("g++ -g -o " + os.path.join(self.driver_dir, "driver") +
                  " " + os.path.join(self.driver_dir, "*.cpp"))

        for slot_name, slot_interface in self.phase.algorithm_slots.items():
            algorithm_path = os.path.join(self.execution_dir, "algorithms", slot_name)
            shutil.copytree(
                os.path.join(self.phase.testcase.prepared_dir, "interfaces", slot_interface),
                algorithm_path
            )
            shutil.copy(
                slots[slot_name],
                os.path.join(algorithm_path, "algorithm.cpp")
            )
            os.system("g++ -g -o " + os.path.join(algorithm_path, "algorithm") +
                      " " + os.path.join(algorithm_path, "*.cpp"))

        os.mkdir(os.path.join(self.execution_dir, "read_files"))

        shutil.copyfile(
            os.path.join(self.phase.phase_dir, "parameter.txt"),
            os.path.join(self.execution_dir, "parameter.txt"))

        supervisor.Supervisor(self.execution_dir).run()

        shutil.copyfile(
            os.path.join(self.execution_dir, "summary.txt"),
            os.path.join(output_dir, "summary.txt"))


class PhaseEvaluation:

    def __init__(self, testcase, conf):
        self.testcase = testcase
        self.conf = conf
        self.name = conf["name"]
        self.algorithm_slots = conf["slots"]
        self.driver_name = conf["driver"]
        self.driver_dir = os.path.join(testcase.prepared_dir, "drivers", self.driver_name)
        self.phase_dir = os.path.join(testcase.testcase_dir, "phases", self.name)
        self.output_dir = os.path.join(testcase.output_dir, "phases", self.name)

    def run(self, slots):
        os.makedirs(self.output_dir, exist_ok=True)

        with tempfile.TemporaryDirectory() as execution_dir:
            PhaseExecution(self, execution_dir).execute(slots, self.output_dir)


class TestcaseEvaluation:

    def __init__(self, prepared_dir, name, evaluation_dir):
        self.prepared_dir = prepared_dir

        self.name = name

        self.testcase_dir = os.path.join(prepared_dir, "testcases", name)
        self.output_dir = os.path.join(evaluation_dir, "testcases", name)

        self.phases_conf_path = os.path.join(self.testcase_dir, "phases.yaml")

        self.load_phases()

    def load_phases(self):
        self.phases_conf = yaml.safe_load(open(self.phases_conf_path))

    def get_phase(self, phase_name):
        phase_conf = next(p for p in self.phases_conf if p["name"] == phase_name)
        return PhaseEvaluation(self, phase_conf)


def main():
    args = docopt(__doc__)

    slots = {}
    for slot in args["<slot:submission>"]:
        name, filename = slot.split(":", 2)
        slots[name] = filename

    output_dir = args["--output"]
    if output_dir is None:
        output_dir = "evaluation_" + datetime.now().strftime("%Y%m%d%H%M%S")
        os.mkdir(output_dir)

    TestcaseEvaluation(args["--input"], args["<testcase>"], output_dir).get_phase(args["--phase"]).run(slots)

