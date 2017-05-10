import os
import shutil
import sys

import pkg_resources
import yaml
from jinja2 import Environment, PackageLoader

from taskwizard.definition.task import TaskDefinition
from taskwizard.language.cpp import preparer as cpp_preparer


languages = {
    "cpp": cpp_preparer
}


class ModulePreparer:

    def __init__(self, problem_preparer, module):
        self.problem_preparer = problem_preparer
        self.module = module
        self.output_dir = os.path.join(problem_preparer.prepared_dir, "modules", module.name)

    def prepare(self):
        delegate = languages[self.module.language].ModulePreparer(self.problem_preparer, self.module, self.output_dir)
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


class ProblemPreparer:

    def __init__(self, definition_dir, output_dir):
        self.definition_dir = definition_dir
        self.prepared_dir = os.path.join(output_dir, "build", "prepared")
        self.yaml_file = os.path.join(self.prepared_dir, "problem.yaml")

    def parse_task(self):
        text = open(os.path.join(self.definition_dir, "task.txt")).read()
        return TaskDefinition.parse(text)

    def prepare(self):
        self.task = self.parse_task()

        shutil.rmtree(self.prepared_dir, ignore_errors=True)
        os.makedirs(self.prepared_dir)

        os.mkdir(os.path.join(self.prepared_dir, "modules"))
        for module in self.task.modules:
            ModulePreparer(self, module).prepare()

        os.mkdir(os.path.join(self.prepared_dir, "interfaces"))
        for interface in self.task.interfaces:
            InterfacePreparer(self, interface).prepare()

        data = {
            "modules": list(self.task.modules.keys()),
            "interfaces": list(self.task.interfaces.keys())
            }
        yaml.safe_dump(data, open(self.yaml_file, "w"))
