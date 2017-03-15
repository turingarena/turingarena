from jinja2 import Environment, PackageLoader
import os
import shutil
import subprocess
import sys
import yaml


class SupportCompiler:

    def __init__(self, problem, input_dir, output_dir):
        self.problem = problem
        self.input_dir = input_dir
        self.output_dir = output_dir

    def compile_support(self):
        os.mkdir(self.output_dir)

        for f in os.listdir(self.input_dir):
            if not f.endswith(".cpp"):
                continue
            command = "g++ -c -g %s -o %s.o" % (
                os.path.join(self.input_dir, f),
                os.path.join(self.output_dir, os.path.splitext(f)[0]))
            print(command)
            subprocess.run(command, shell=True, check=True)


class DriverCompiler(SupportCompiler):

    def __init__(self, problem, driver_name):
        super().__init__(
            problem,
            os.path.join(problem.prepared_dir, "drivers", driver_name),
            os.path.join(problem.compiled_dir, "drivers", driver_name),
        )
        self.driver_name = driver_name

    def compile(self):
        self.compile_support()
        command = "g++ -g %s -o %s" % (
            os.path.join(self.output_dir, "*.o"),
            os.path.join(self.output_dir, "driver"))
        print(command)
        subprocess.run(command, shell=True, check=True)


class InterfaceCompiler(SupportCompiler):

    def __init__(self, problem, interface_name):
        super().__init__(
            problem,
            os.path.join(problem.prepared_dir, "interfaces", interface_name),
            os.path.join(problem.compiled_dir, "interfaces", interface_name),
        )
        self.interface_name = interface_name

    def compile(self):
        self.compile_support()


class ProblemCompiler:

    def __init__(self, input_dir, output_dir):
        self.prepared_dir = os.path.join(input_dir, "build", "prepared")
        self.compiled_dir = os.path.join(output_dir, "build", "compiled")

        self.prepared_yaml_file = os.path.join(self.prepared_dir, "problem.yaml")
        self.compiled_yaml_file = os.path.join(self.compiled_dir, "problem.yaml")

    def compile(self):
        data = yaml.safe_load(open(self.prepared_yaml_file))

        shutil.rmtree(self.compiled_dir, ignore_errors=True)
        os.mkdir(self.compiled_dir)

        shutil.copyfile(self.prepared_yaml_file, self.compiled_yaml_file)

        os.mkdir(os.path.join(self.compiled_dir, "drivers"))
        for name in data["drivers"]:
            DriverCompiler(self, name).compile()

        os.mkdir(os.path.join(self.compiled_dir, "interfaces"))
        for name in data["interfaces"]:
            InterfaceCompiler(self, name).compile()

        shutil.copytree(
            os.path.join(self.prepared_dir, "scenarios"),
            os.path.join(self.compiled_dir, "scenarios"))

