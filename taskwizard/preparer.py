"""Task Compiler.

Usage:
  taskcc prepare [-i <input-output_dir>] -o <output-output_dir>
  taskcc stubs [-i <input-output_dir>] -o <output-file>
  taskcc stub (driver|interface <name>) [-i <input-output_dir>] [-o <output-file>]
  taskcc -h | --help

Options:
  -h --help          Show this screen.
  --version          Show version.
  prepare            Create the problem prepared folder
  stub               Create the stub of driver/interfaces
  name               The name of the interface to use.
  -i --input=<output_dir>   Path to task source directory [default: .].
  -o --output=<out>  Path to output file/directory
"""

from docopt import docopt
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

    def __init__(self, problem):
        super().__init__(problem, os.path.join(problem.prepared_dir, "driver"))

    def get_type(self):
        return "driver"

    def get_template_args(self):
        return {"task": self.problem.task}

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

        env = Environment(loader=PackageLoader("taskwizard.compiler", "templates"))
        template = env.get_template(os.path.join("stub", "interface.cpp.j2"))
        template.stream(interface=self.interface).dump(output)
        if output_path is not None:
            output.close()


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

        DriverPreparer(self).prepare()

        os.mkdir(os.path.join(self.prepared_dir, "interfaces"))
        for interface in self.task.interfaces.values():
            InterfacePreparer(self, interface).prepare()

        task_yaml = open(os.path.join(self.prepared_dir, "task.yaml"), "w")
        yaml.safe_dump(
            {
                "slots": {
                    "solution": {
                        "interface": "aplusb"
                    }
                }
            }, task_yaml)


def main():
    args = docopt(__doc__)

    if args["prepare"]:
        ProblemPreparer(args["--input"], args["--output"]).prepare()

    if args["stub"] or args["stubs"]:
        raise NotImplementedError("not yet supported")
