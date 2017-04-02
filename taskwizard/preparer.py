import os
import shutil
import sys

import pkg_resources
import yaml
from jinja2 import Environment, PackageLoader

from taskwizard.definition.semantics import Semantics
from taskwizard.language.cpp import preparer as cpp_preparer
from taskwizard.parser import TaskParser


languages = {
    "cpp": cpp_preparer
}


class DriverPreparer:

    def __init__(self, problem_preparer, driver):
        self.problem_preparer = problem_preparer
        self.driver = driver
        self.output_dir = os.path.join(problem_preparer.prepared_dir, "drivers", driver.name)

    def prepare(self):
        delegate = languages[self.driver.language].DriverPreparer(self.problem_preparer, self.driver, self.output_dir)
        delegate.prepare()


class InterfacePreparer:

    def __init__(self, problem_preparer, interface):
        self.problem_preparer = problem_preparer
        self.interface = interface
        self.output_dir = os.path.join(problem_preparer.prepared_dir, "interfaces", interface.name)

    def prepare(self):
        os.mkdir(self.output_dir)
        for language, preparer in languages.items():
            delegate = preparer.InterfacePreparer(self.problem_preparer, self.interface, os.path.join(self.output_dir, language))
            delegate.prepare()


class TestPhasePreparer:

    def __init__(self, scenario, phase):
        self.scenario = scenario
        self.phase = phase
        self.output_dir = os.path.join(scenario.output_dir, "phases", phase.name)

    def prepare(self):
        os.mkdir(self.output_dir)

        phase_yaml_file = open(os.path.join(self.output_dir, "phase.yaml"), "w")
        yaml.safe_dump({
            "driver": self.phase.driver_name,
            "slots": {
                slot.name: slot.interface_name
                for slot in self.phase.slots.values()}}, phase_yaml_file)

        env = Environment(loader=PackageLoader("taskwizard", "templates"))
        output = open(os.path.join(self.output_dir, "parameter.txt"), "w")
        # TODO: fill parameter.txt


class TestCasePreparer:

    def __init__(self, problem_preparer, test_case):
        self.problem_preparer = problem_preparer
        self.test_case = test_case
        self.output_dir = os.path.join(problem_preparer.prepared_dir, "testcases", test_case.name)

    def prepare(self):
        os.mkdir(self.output_dir)

        os.mkdir(os.path.join(self.output_dir, "phases"))

        for phase in self.test_case.phases.values():
            p = TestPhasePreparer(self, phase)
            p.prepare()

        test_case_yaml_file = open(os.path.join(self.output_dir, "testcase.yaml"), "w")
        yaml.safe_dump({
            "phases": list(self.test_case.phases.keys())}, test_case_yaml_file)


class ProblemPreparer:

    def __init__(self, definition_dir, output_dir):
        self.definition_dir = definition_dir
        self.prepared_dir = os.path.join(output_dir, "build", "prepared")
        self.yaml_file = os.path.join(self.prepared_dir, "problem.yaml")

    def parse_task(self):
        parser = TaskParser(semantics=Semantics())
        text = open(os.path.join(self.definition_dir, "task.txt")).read()
        return parser.parse(text)

    def prepare(self):
        self.task = self.parse_task()

        shutil.rmtree(self.prepared_dir, ignore_errors=True)
        os.makedirs(self.prepared_dir)

        os.mkdir(os.path.join(self.prepared_dir, "drivers"))
        for driver in self.task.drivers.values():
            DriverPreparer(self, driver).prepare()

        os.mkdir(os.path.join(self.prepared_dir, "interfaces"))
        for interface in self.task.interfaces.values():
            InterfacePreparer(self, interface).prepare()

        os.mkdir(os.path.join(self.prepared_dir, "testcases"))
        for test_case in self.task.test_cases.values():
            TestCasePreparer(self, test_case).prepare()

        data = {
            "drivers": list(self.task.drivers.keys()),
            "interfaces": list(self.task.interfaces.keys()),
            "testcases": list(self.task.test_cases.keys()),
            }
        yaml.safe_dump(data, open(self.yaml_file, "w"))
