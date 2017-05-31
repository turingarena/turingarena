import os
import shutil

import pkg_resources
from jinja2.environment import Environment
from jinja2.loaders import PackageLoader


class ModulePreparer:

    def __init__(self, problem_preparer, module, output_dir):
        self.problem_preparer = problem_preparer
        self.module = module
        self.output_dir = output_dir

    def prepare(self):
        shutil.copytree(
            pkg_resources.resource_filename("taskwizard.language.cpp", "module_lib"),
            self.output_dir
        )

        shutil.copyfile(
            os.path.join(self.problem_preparer.definition_dir, self.module.source),
            os.path.join(self.output_dir, "module.cpp"),
        )


class InterfacePreparer:

    def __init__(self, problem_preparer, interface, output_dir):
        self.problem_preparer = problem_preparer
        self.interface = interface
        self.output_dir = output_dir

    def prepare(self):
        os.mkdir(self.output_dir)
