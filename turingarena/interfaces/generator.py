import os
import shutil

import turingarena.interfaces.drivergen.python.main as python_drivergen
import turingarena.interfaces.supportgen.cpp.main as cpp_supportgen

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

        self.interfaces_dir = os.path.join(self.output_dir, "interfaces")
        self.runtime_dir = os.path.join(self.output_dir, "cpp")

    def generate(self):
        os.makedirs(self.output_dir, exist_ok=True)

        # cleanup
        shutil.rmtree(self.output_dir, ignore_errors=True)
        os.mkdir(self.output_dir)

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
        os.mkdir(self.runtime_dir)
        for language, generator in lang_drivergen.items():
            language_dir = os.path.join(self.runtime_dir, language)
            os.mkdir(language_dir)
            generator(self.task, language_dir).generate()
