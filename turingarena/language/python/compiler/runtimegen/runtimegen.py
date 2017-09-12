import os

from turingarena.compiler.codegen.utils import write_to_file

from turingarena.compiler.codegen.drivergen import AbstractDriverGenerator, AbstractInterfaceDriverGenerator
from turingarena.language.python.compiler.runtimegen.interface import InterfaceGenerator


class InterfaceDriverGenerator(AbstractInterfaceDriverGenerator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.module_path = os.path.join(
            self.driver_generator.package_dir,
            self.interface.name + ".py"
        )

    def generate(self):
        module_file = open(self.module_path, "w")
        write_to_file(self.generate_module(), module_file)

    def generate_module(self):
        yield "from __future__ import print_function"
        yield "from turingarena.runtime.driver import *"
        yield "from turingarena.runtime.data import *"
        yield
        yield from self.interface.accept(InterfaceGenerator())


class DriverGenerator(AbstractDriverGenerator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.package_dir = os.path.join(self.dest_dir, "interfaces")

    def generate(self):
        os.mkdir(self.package_dir)

        for interface in self.task.interfaces:
            self.generate_interface(interface)

    def generate_interface(self, interface):
        InterfaceDriverGenerator(self, interface).generate()
