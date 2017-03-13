from jinja2 import Environment, PackageLoader
import os
import pkg_resources
import shutil
import sys
import yaml

from taskwizard.parser import TaskParser
from taskwizard.semantics import Semantics


class SupportPreparer:

    def __init__(self, problem, output_dir):
        self.problem = problem
        self.output_dir = output_dir

    def prepare_support(self):
        env = Environment(loader=PackageLoader("taskwizard", "templates"))

        template_relative_dir = "support/" + self.get_type()
        template_dir = pkg_resources.resource_filename("taskwizard", "templates/" + template_relative_dir)

        os.mkdir(self.output_dir)

        for f in os.listdir(template_dir):
            ext = ".j2"
            if f.endswith(ext):
                template = env.get_template(os.path.join(template_relative_dir, f))
                output = open(os.path.join(self.output_dir, f[:-len(ext)]), "w")
                template.stream(**self.get_template_args()).dump(output)
            else:
                shutil.copyfile(os.path.join(template_dir, f), os.path.join(self.output_dir, f))


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

    def __init__(self, testcase, phase):
        self.testcase = testcase
        self.phase = phase
        self.output_dir = os.path.join(testcase.output_dir, "phases", phase.name)

    def prepare(self):
        os.mkdir(self.output_dir)
        env = Environment(loader=PackageLoader("taskwizard", "templates"))
        template = env.get_template(os.path.join("parameter", "parameter.txt.j2"))
        output = open(os.path.join(self.output_dir, "parameter.txt"), "w")
        template.stream(command=self.phase.driver_command).dump(output)

    def get_yaml(self):
        return {
            "name": self.phase.name,
            "driver": self.phase.driver_name,
            "slots": {
                slot.name: slot.interface_name
                for slot in self.phase.slots.values()}}


class TestcasePreparer:

    def __init__(self, problem, testcase):
        self.problem = problem
        self.testcase = testcase
        self.output_dir = os.path.join(problem.prepared_dir, "testcases", testcase.name)

    def prepare(self):
        os.mkdir(self.output_dir)

        os.mkdir(os.path.join(self.output_dir, "phases"))
        phases = []
        for phase in self.testcase.phases.values():
            p = PhasePreparer(self, phase)
            p.prepare()
            phases += [p.get_yaml()]

        phases_yaml_file = open(os.path.join(self.output_dir, "phases.yaml"), "w")
        yaml.safe_dump(phases, phases_yaml_file)


class ProblemPreparer:

    def __init__(self, task_dir, prepared_dir):
        self.task_dir = task_dir
        self.prepared_dir = prepared_dir

    def parse_task(self):
        parse = TaskParser(semantics=Semantics())
        text = open(os.path.join(self.task_dir, "task.txt")).read()
        return parse.parse(text)

    def prepare(self):
        self.task = self.parse_task()

        os.mkdir(self.prepared_dir)

        os.mkdir(os.path.join(self.prepared_dir, "drivers"))
        for driver in self.task.drivers.values():
            DriverPreparer(self, driver).prepare()

        os.mkdir(os.path.join(self.prepared_dir, "interfaces"))
        for interface in self.task.interfaces.values():
            InterfacePreparer(self, interface).prepare()

        os.mkdir(os.path.join(self.prepared_dir, "testcases"))
        for testcase in self.task.testcases.values():
            TestcasePreparer(self, testcase).prepare()
