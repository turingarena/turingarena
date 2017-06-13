import os
import shutil

from taskwizard.language.cpp.supportgen import supportgen as cpp_supportgen
from taskwizard.language.python.drivergen import drivergen as python_drivergen


lang_supportgen = {
    "cpp": cpp_supportgen.SupportGenerator
}


lang_drivergen = {
    "python": python_drivergen.DriverGenerator,
}


class CodeGenerator:

    def __init__(self, task, output_dir):
        self.task = task
        self.output_dir = output_dir

        self.generated_dir = os.path.join(self.output_dir, "generated")

        self.interfaces_dir = os.path.join(self.generated_dir, "interfaces")
        self.driver_dir = os.path.join(self.generated_dir, "driver")

    def generate(self):
        os.makedirs(self.generated_dir, exist_ok=True)

        # cleanup
        shutil.rmtree(self.generated_dir, ignore_errors=True)
        os.mkdir(self.generated_dir)

        self.generate_interfaces_support()
        self.generate_driver()

    def generate_interfaces_support(self):
        os.mkdir(self.interfaces_dir)
        for interface in self.task.interfaces:
            interface_dir = os.path.join(self.interfaces_dir, interface.name)
            os.mkdir(interface_dir)
            for language, generator in lang_supportgen.items():
                language_dir = os.path.join(interface_dir, language)
                os.mkdir(language_dir)
                generator(self.task, interface, language_dir).generate()

    def generate_driver(self):
        os.mkdir(self.driver_dir)
        for language, generator in lang_drivergen.items():
            language_dir = os.path.join(self.driver_dir, language)
            os.mkdir(language_dir)
            generator(self.task, language_dir).generate()
