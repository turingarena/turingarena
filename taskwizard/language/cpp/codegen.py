import os

from taskwizard.generation.codegen import AbstractDriverGenerator, AbstractSupportGenerator
from taskwizard.generation.utils import indent_all, write_to_file
from taskwizard.language.cpp.blocks import generate_block
from taskwizard.language.cpp.declarations import build_declaration, build_parameter
from taskwizard.language.cpp.types import generate_base_type


class DriverGenerator(AbstractDriverGenerator):

    def generate(self):
        pass


class InterfaceItemGenerator:

    def visit_variable_declaration(self, declaration):
        yield build_declaration(declaration)

    def visit_function_declaration(self, definition):
        yield "{return_type} {name}({arguments});".format(
            return_type=generate_base_type(definition.return_type),
            name=definition.declarator.name,
            arguments=', '.join(build_parameter(p) for p in definition.parameters)
        )

    def visit_main_definition(self, definition):
        yield "int main() {"
        yield from indent_all(generate_block(definition.block))
        yield "}"


class SupportGenerator(AbstractSupportGenerator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.include_file_path = os.path.join(self.dest_dir, "main.h")
        self.main_file_path = os.path.join(self.dest_dir, "main.cpp")

    def generate(self):
        main_file = open(self.main_file_path, "w")
        write_to_file(self.generate_main_file(), main_file)

    def generate_main_file(self):
        yield "#include <cstdio>"
        generator = InterfaceItemGenerator()
        for item in self.interface.interface_items:
            yield
            yield from item.accept(generator)


