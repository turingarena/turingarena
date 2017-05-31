import os

from taskwizard.language.cpp.blocks import generate_support_block
from taskwizard.language.cpp.declarations import generate_declaration, generate_parameter
from taskwizard.language.cpp.types import generate_base_type
from taskwizard.language.cpp.utils import indent


class DriverGenerator:

    def __init__(self, task, dest_dir):
        self.task = task
        self.dest_dir = dest_dir

    def generate(self):
        pass


class SupportGenerator:

    def __init__(self, task, interface, dest_dir):
        self.task = task
        self.interface = interface
        self.dest_dir = dest_dir

        self.include_file_path = os.path.join(self.dest_dir, "main.h")
        self.main_file_path = os.path.join(self.dest_dir, "main.cpp")

    def generate(self):
        main_file = open(self.main_file_path, "w")
        for line in self.generate_main_file():
            print(line, file=main_file)

    def generate_main_file(self):
        yield "#include <cstdio>"
        yield ""
        yield from self.generate_global_declarations()
        yield ""
        yield from self.generate_prototypes()
        yield ""
        yield from self.generate_main_function()

    def generate_global_declarations(self):
        for d in self.interface.variables:
            yield from generate_declaration(d)

    def generate_prototypes(self):
        for f in self.interface.functions:
            yield from self.generate_function_declaration(f)

    def generate_function_declaration(self, function):
        yield "{return_type} {name}({arguments});".format(
            return_type=generate_base_type(function.return_type),
            name=function.name,
            arguments=', '.join(generate_parameter(p) for p in function.parameters)
        )

    def generate_main_function(self):
        yield "int main() {"
        yield from indent(self.generate_main_block())
        yield "}"

    def generate_main_block(self):
        yield from generate_support_block(self.interface.main_definition.block)


