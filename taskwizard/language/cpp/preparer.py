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
            pkg_resources.resource_filename("taskwizard.language.cpp", "module_static"),
            self.output_dir
        )

        shutil.copyfile(
            os.path.join(self.problem_preparer.definition_dir, self.module.source),
            os.path.join(self.output_dir, "module.cpp"),
        )

        env = Environment(
            loader=PackageLoader("taskwizard.language.cpp"),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
            block_start_string="/*{%",
            block_end_string="%}*/",
            variable_start_string="/*{{",
            variable_end_string="}}*/",
        )

        env.get_template("module.h").stream(task=self.problem_preparer.task, module=self.module).dump(
                open(os.path.join(self.output_dir, "module.h"), "w")
        )

        env.get_template("module_support.cpp").stream(task=self.problem_preparer.task, module=self.module).dump(
                open(os.path.join(self.output_dir, "support.cpp"), "w")
        )

        for interface in self.problem_preparer.task.interfaces:
            env.get_template("module_interface_support.cpp").stream(task=self.problem_preparer.task, module=self.module, interface=interface).dump(
                    open(os.path.join(self.output_dir, "%s_support.cpp" % interface.name), "w")
            )


class InterfacePreparer:

    def __init__(self, problem_preparer, interface, output_dir):
        self.problem_preparer = problem_preparer
        self.interface = interface
        self.output_dir = output_dir

    def prepare(self):
        os.mkdir(self.output_dir)

        env = Environment(
            loader=PackageLoader("taskwizard.language.cpp"),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

        env.get_template("interface.h").stream(task=self.problem_preparer.task, interface=self.interface).dump(
                open(os.path.join(self.output_dir, "%s.h" % self.interface.name), "w")
        )

        env.get_template("interface_support.cpp").stream(task=self.problem_preparer.task, interface=self.interface).dump(
                open(os.path.join(self.output_dir, "support.cpp"), "w")
        )
