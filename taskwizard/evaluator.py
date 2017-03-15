from datetime import datetime
from docopt import docopt
import os
import shutil
import subprocess
import tempfile
import yaml

from taskwizard import supervisor


class PhaseExecution:

    def __init__(self, case_phase, execution_dir):
        self.case_phase = case_phase
        self.phase = case_phase.phase
        self.scenario = self.phase.scenario
        self.problem = self.scenario.problem

        self.execution_dir = execution_dir
        self.driver_dir = os.path.join(self.execution_dir, "driver")

    def execute(self, output_dir, slots):
        os.mkdir(os.path.join(self.execution_dir, "algorithms"))
        shutil.copytree(
            self.phase.driver_dir,
            self.driver_dir
        )
        command = "g++ -g %s -o %s" % (
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
            command = "g++ -g %s -o %s" % (
                os.path.join(algorithm_path, "*.cpp"),
                os.path.join(algorithm_path, "algorithm"))
            print(command)
            subprocess.run(command, shell=True, check=True)

        os.mkdir(os.path.join(self.execution_dir, "read_files"))

        shutil.copyfile(
            os.path.join(self.phase.input_dir, "parameter.txt"),
            os.path.join(self.execution_dir, "parameter.txt"))

        print(self.case_phase.seed, file=open(os.path.join(self.execution_dir, "seed.txt"), "w"))

        supervisor.Supervisor(self.execution_dir).run()

        shutil.copyfile(
            os.path.join(self.execution_dir, "summary.txt"),
            os.path.join(output_dir, "summary.txt"))


class CasePhaseEvaluator:

    def __init__(self, phase, seed):
        self.phase = phase
        self.seed = seed

        self.output_dir = os.path.join(
            phase.scenario.problem.evaluation_dir,
            "testcases", phase.scenario.name, str(seed),
            "phases", phase.name)

    def evaluate(self, **kwargs):
        print("Evaluating phase '%s' with seed %3d/%d..." % (
            self.phase.name,
            self.seed,
            self.phase.scenario.cases))

        os.makedirs(self.output_dir, exist_ok=True)
        with tempfile.TemporaryDirectory() as execution_dir:
            PhaseExecution(self, execution_dir).execute(self.output_dir, **kwargs)


class PhaseEvaluator:

    def __init__(self, scenario, name):
        self.scenario = scenario
        self.name = name

        self.input_dir = os.path.join(scenario.input_dir, "phases", name)
        self.phase_yaml_file = os.path.join(self.input_dir, "phase.yaml")

    def evaluate(self, **kwargs):
        print("Evaluating phase '%s'..." % self.name)

        data = yaml.safe_load(open(self.phase_yaml_file))

        self.driver_name = data["driver"]
        self.driver_dir = os.path.join(
            self.scenario.problem.prepared_dir, "drivers", self.driver_name)

        self.algorithm_slots = {}
        for slot_name, slot_conf in data["slots"].items():
            self.algorithm_slots[slot_name] = slot_conf

        for seed in range(1, 1 + self.scenario.cases):
            CasePhaseEvaluator(self, seed).evaluate(**kwargs)


class ScenarioEvaluator:

    def __init__(self, problem, name):
        self.problem = problem
        self.name = name

        self.input_dir = os.path.join(problem.prepared_dir, "scenarios", name)

        self.scenario_yaml_file = os.path.join(self.input_dir, "scenario.yaml")

    def evaluate(self, **kwargs):
        print("Evaluating scenario '%s'..." % self.name)

        data = yaml.safe_load(open(self.scenario_yaml_file))

        self.phases = data["phases"]
        self.cases = int(data["cases"])

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

        for name in data["scenarios"]:
            ScenarioEvaluator(self, name).evaluate(**kwargs)

