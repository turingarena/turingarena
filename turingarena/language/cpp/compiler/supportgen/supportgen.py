import os

from turingarena.compiler.codegen.supportgen import AbstractSupportGenerator
from turingarena.compiler.codegen.utils import indent_all, write_to_file, indent

from turingarena.language.cpp.compiler.supportgen.declarations import build_declaration, build_parameter
from turingarena.language.cpp.compiler.supportgen.types import generate_base_type
from turingarena.language.cpp.compiler.supportgen.blocks import generate_block


class InterfaceItemGenerator:

    def visit_variable_declaration(self, declaration):
        yield build_declaration(declaration)

    def visit_function_declaration(self, decl):
        yield "{return_type} {name}({arguments});".format(
            return_type=generate_base_type(decl.return_type),
            name=decl.declarator.name,
            arguments=', '.join(build_parameter(p) for p in decl.parameters)
        )

    def visit_callback_declaration(self, decl):
        yield "{return_type} {name}({arguments})".format(
            return_type=generate_base_type(decl.return_type),
            name=decl.declarator.name,
            arguments=', '.join(build_parameter(p) for p in decl.parameters)
        ) + " {"
        yield indent(r'printf("{name}\n");').format(name=decl.declarator.name)
        yield indent('fflush(stdout);')
        yield from indent_all(generate_block(decl.block))
        yield "}"

    def visit_main_declaration(self, definition):
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


