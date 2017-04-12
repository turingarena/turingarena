import os
import shutil

import pkg_resources
from jinja2.environment import Environment
from jinja2.loaders import PackageLoader


class DriverPreparer:

    def __init__(self, problem_preparer, driver, output_dir):
        self.problem_preparer = problem_preparer
        self.driver = driver
        self.output_dir = output_dir

    def prepare(self):
        shutil.copytree(
            pkg_resources.resource_filename("taskwizard.language.cpp", "driver_static"),
            self.output_dir
        )

        shutil.copyfile(
            os.path.join(self.problem_preparer.definition_dir, self.driver.source),
            os.path.join(self.output_dir, "driver.cpp"),
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

        env.get_template("driver.h").stream(task=self.problem_preparer.task, driver=self.driver).dump(
                open(os.path.join(self.output_dir, "driver.h"), "w")
        )

        env.get_template("driver_support.cpp").stream(task=self.problem_preparer.task, driver=self.driver).dump(
                open(os.path.join(self.output_dir, "support.cpp"), "w")
        )

        for interface in self.problem_preparer.task.interfaces:
            env.get_template("driver_interface_support.cpp").stream(task=self.problem_preparer.task, driver=self.driver, interface=interface).dump(
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
