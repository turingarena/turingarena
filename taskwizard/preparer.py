from jinja2 import Environment, PackageLoader
import os
import pkg_resources
import shutil
import sys
import yaml
import subprocess

from taskwizard.parser import TaskParser
from taskwizard.semantics import Semantics


class SupportPreparer:

    def __init__(self, problem, output_dir):
        self.problem = problem
        self.output_dir = output_dir

    def prepare_support(self):
        env = Environment(
            loader=PackageLoader("taskwizard", "templates"),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

        template_relative_dir = "support/" + self.get_type()
        template_dir = pkg_resources.resource_filename("taskwizard", "templates/" + template_relative_dir)

        os.mkdir(self.output_dir)

        for f in os.listdir(template_dir):
            template = env.get_template(os.path.join(template_relative_dir, f))
            output = open(os.path.join(self.output_dir, f), "w")
            template.stream(**self.get_template_args()).dump(output)


class DriverPreparer(SupportPreparer):

    def __init__(self, problem, driver):
        super().__init__(problem, os.path.join(problem.prepared_dir, "drivers", driver.name))
        self.driver = driver

    def get_type(self):
        return "driver"

    def get_template_args(self):
        return {"task": self.problem.task, "driver": self.driver}

    def prepare(self):
        self.prepare_support()
        shutil.copyfile(
            os.path.join(self.problem.task_dir, "driver.cpp"),
            os.path.join(self.output_dir, "driver.cpp")
        )


class InterfacePreparer(SupportPreparer):

    def __init__(self, problem, interface):
        super().__init__(problem, os.path.join(problem.prepared_dir, "interfaces", interface.name))
        self.interface = interface

    def get_type(self):
        return "interface"

    def get_template_args(self):
        return {"interface": self.interface}

    def prepare(self):
        self.prepare_support()

    def generate_stub(self, output_path):
        output = sys.stdout
        if output_path is not None:
            output = open(output_path, "w")

        env = Environment(loader=PackageLoader("taskwizard", "templates"))
        template = env.get_template(os.path.join("stub", "interface.cpp.j2"))
        template.stream(interface=self.interface).dump(output)
        if output_path is not None:
            output.close()


class PhasePreparer:

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
        template = env.get_template(os.path.join("parameter", "parameter.txt.j2"))
        output = open(os.path.join(self.output_dir, "parameter.txt"), "w")
        template.stream(command=self.phase.driver_command).dump(output)


class ScenarioPreparer:

    def __init__(self, problem, scenario):
        self.problem = problem
        self.scenario = scenario
        self.output_dir = os.path.join(problem.prepared_dir, "scenarios", scenario.name)

    def prepare(self):
        os.mkdir(self.output_dir)

        os.mkdir(os.path.join(self.output_dir, "phases"))

        for phase in self.scenario.phases.values():
            p = PhasePreparer(self, phase)
            p.prepare()

        scenario_yaml_file = open(os.path.join(self.output_dir, "scenario.yaml"), "w")
        yaml.safe_dump({
            "cases": 10,
            "phases": list(self.scenario.phases.keys())}, scenario_yaml_file)


class ProblemPreparer:

    def __init__(self, task_dir, output_dir):
        self.task_dir = task_dir
        self.prepared_dir = os.path.join(output_dir, "build", "prepared")
        self.yaml_file = os.path.join(self.prepared_dir, "problem.yaml")

    def parse_task(self):
        parse = TaskParser(semantics=Semantics())
        text = open(os.path.join(self.task_dir, "task.txt")).read()
        return parse.parse(text)

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

        os.mkdir(os.path.join(self.prepared_dir, "scenarios"))
        for scenario in self.task.scenarios.values():
            ScenarioPreparer(self, scenario).prepare()

        data = {
            "drivers": list(self.task.drivers.keys()),
            "interfaces": list(self.task.interfaces.keys()),
            "scenarios": list(self.task.scenarios.keys()),
            }
        yaml.safe_dump(data, open(self.yaml_file, "w"));
