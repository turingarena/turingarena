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
