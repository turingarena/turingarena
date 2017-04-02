from datetime import datetime
from docopt import docopt
import os
import shutil
import subprocess
import tempfile
import yaml

from taskwizard import supervisor


class PhaseExecution:

    def __init__(self, phase, execution_dir):
        self.phase = phase
        self.case = phase.case
        self.problem = self.case.problem

        self.execution_dir = execution_dir
        self.driver_dir = os.path.join(self.execution_dir, "driver")

    def execute(self, output_dir, slots):
        os.mkdir(os.path.join(self.execution_dir, "algorithms"))
        shutil.copytree(
            self.phase.driver_dir,
            self.driver_dir
        )
        command = "g++ -std=c++11 -g %s -o %s" % (
            os.path.join(self.driver_dir, "*.cpp"),
            os.path.join(self.driver_dir, "driver"))
        print(command)
        subprocess.run(command, shell=True, check=True)

        for slot_name, slot_interface in self.phase.algorithm_slots.items():
            algorithm_path = os.path.join(self.execution_dir, "algorithms", slot_name)
            shutil.copytree(
                os.path.join(self.problem.prepared_dir, "interfaces", slot_interface),
                algorithm_path
            )
            shutil.copy(
                slots[slot_name],
                os.path.join(algorithm_path, "algorithm.cpp")
            )
            command = "g++ -std=c++11 -g %s -o %s" % (
                os.path.join(algorithm_path, "*.cpp"),
                os.path.join(algorithm_path, "algorithm"))
            print(command)
            subprocess.run(command, shell=True, check=True)

        os.mkdir(os.path.join(self.execution_dir, "read_files"))

        shutil.copyfile(
            os.path.join(self.phase.input_dir, "parameter.txt"),
            os.path.join(self.execution_dir, "parameter.txt"))

        print(self.test_phase.seed, file=open(os.path.join(self.execution_dir, "seed.txt"), "w"))

        supervisor.Supervisor(self.execution_dir).run()

        shutil.copyfile(
            os.path.join(self.execution_dir, "result.txt"),
            os.path.join(output_dir, "result.txt"))


class PhaseEvaluator:

    def __init__(self, case, name):
        self.case = case
        self.name = name

        self.output_dir = os.path.join(case.output_dir, "phases", name)
        self.input_dir = os.path.join(case.input_dir, "phases", name)
        self.phase_yaml_file = os.path.join(self.input_dir, "phase.yaml")

        data = yaml.safe_load(open(self.phase_yaml_file))

        self.driver_name = data["driver"]
        self.driver_dir = os.path.join(
                self.case.problem.prepared_dir, "drivers", self.driver_name)

        self.algorithm_slots = {}
        for slot_name, slot_conf in data["slots"].items():
            self.algorithm_slots[slot_name] = slot_conf

    def evaluate(self, **kwargs):
        print("Evaluating phase '%s'..." % self.name)
        os.makedirs(self.output_dir, exist_ok=True)

        with tempfile.TemporaryDirectory() as execution_dir:
            PhaseExecution(self, execution_dir).execute(self.output_dir, **kwargs)


class TestCaseEvaluator:

    def __init__(self, problem, name):
        self.problem = problem
        self.name = name

        self.input_dir = os.path.join(problem.prepared_dir, "testcases", name)
        self.output_dir = os.path.join(problem.evaluation_dir, "testcases", name)

        self.case_yaml_file = os.path.join(self.input_dir, "testcase.yaml")

        data = yaml.safe_load(open(self.case_yaml_file))

        self.phases = data["phases"]

    def evaluate(self, **kwargs):
        print("Evaluating test case '%s'..." % self.name)

        for phase in self.phases:
            PhaseEvaluator(self, phase).evaluate(**kwargs)


class ProblemEvaluator:

    def __init__(self, input_dir, output_dir, name):
        self.id = id
        self.prepared_dir = os.path.join(input_dir, "build", "prepared")
        self.evaluation_dir = os.path.join(output_dir, "evaluations", name)

        self.problem_yaml_file = os.path.join(self.prepared_dir, "problem.yaml")

    def evaluate(self, **kwargs):
        data = yaml.safe_load(open(self.problem_yaml_file))

        os.makedirs(self.evaluation_dir, exist_ok=True)

        for name in data["testcases"]:
            TestCaseEvaluator(self, name).evaluate(**kwargs)

