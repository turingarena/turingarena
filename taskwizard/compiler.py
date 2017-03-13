"""Task Compiler.

Usage:
  taskcc runner [-i <input-dir>] -o <output-dir>
  taskcc stubs [-i <input-dir>] -o <output-file>
  taskcc stub (driver|interface <name>) [-i <input-dir>] [-o <output-file>]
  taskcc -h | --help

Options:
  -h --help          Show this screen.
  --version          Show version.
  runner             Create the task runnable package
  stub               Create the stub of driver/interfaces
  name               The name of the interface to use.
  -i --input=<dir>   Path to task source directory [default: .].
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


class TaskObject:

    def __init__(self, task):
        self.task = task

    def compile_support(self, output_dir):
        env = Environment(loader=PackageLoader("taskwizard.compiler", "templates"))

        template_relative_dir = "support/" + self.get_type()
        template_dir = pkg_resources.resource_filename("taskwizard", "templates/" + template_relative_dir)

        os.mkdir(output_dir)

        for f in os.listdir(template_dir):
            ext = ".j2"
            if f.endswith(ext):
                template = env.get_template(os.path.join(template_relative_dir, f))
                output = open(os.path.join(output_dir, f[:-len(ext)]), "w")
                template.stream(**self.get_template_args()).dump(output)
            else:
                shutil.copyfile(os.path.join(template_dir, f), os.path.join(output_dir, f))


class TaskDriver(TaskObject):

    def __init__(self, task):
        super().__init__(task)

    def get_type(self):
        return "driver"

    def get_template_args(self):
        return {"task": self.task}


class TaskInterface(TaskObject):

    def __init__(self, task, interface):
        super().__init__(task)
        self.interface = interface

    def get_type(self):
        return "interface"

    def get_template_args(self):
        return {"interface": self.interface}

    def generate_stub(self, output_path):
        output = sys.stdout
        if output_path is not None:
            output = open(output_path, "w")

        env = Environment(loader=PackageLoader("taskwizard.compiler", "templates"))
        template = env.get_template(os.path.join("stub", "interface.cpp.j2"))
        template.stream(interface=self.interface).dump(output)
        if output_path is not None:
            output.close()


def make_runner(task, task_source_dir, output_dir):
    os.mkdir(output_dir)

    driver_dir = os.path.join(output_dir, "driver")
    TaskDriver(task).compile_support(driver_dir)
    shutil.copyfile(os.path.join(task_source_dir, "driver.cpp"), os.path.join(driver_dir, "driver.cpp"))

    os.mkdir(os.path.join(output_dir, "interfaces"))

    for interface in task.interfaces.values():
        interface_dir = os.path.join(output_dir, "interfaces", interface.name)
        TaskInterface(task, interface).compile_support(interface_dir)

    task_yaml = open(os.path.join(output_dir, "task.yaml"), "w")
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

    task_source_dir = args["--input"]

    parse = TaskParser(semantics=Semantics())
    text = open(os.path.join(task_source_dir, "task.txt")).read()
    task = parse.parse(text)

    if args["runner"]:
        output_dir = args["--output"]
        make_runner(task, task_source_dir, output_dir)

    if args["stub"]:
        if args["interface"]:
            interface_name = args["<name>"]
            task_object = TaskInterface(task, task.interfaces[interface_name])
        if args["driver"]:
            task_object = TaskDriver(task)

        output_path = args["--output"]
        task_object.generate_stub(output_path)

    if args["stubs"]:
        raise ValueError("not yet supported")
