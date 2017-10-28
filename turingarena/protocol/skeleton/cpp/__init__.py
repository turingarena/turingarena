import os

from turingarena.protocol.codegen.utils import indent_all, write_to_file, indent
from turingarena.protocol.skeleton.cpp.blocks import generate_block
from turingarena.protocol.skeleton.cpp.declarations import build_declaration, build_parameter
from turingarena.protocol.skeleton.cpp.types import build_type_expression
from turingarena.protocol.skeleton.common import AbstractSupportGenerator
from turingarena.protocol.visitor import accept_statement


class InterfaceItemGenerator:
    def visit_var_statement(self, declaration):
        yield build_declaration(declaration)

    def visit_function_statement(self, statement):
        declarator = statement.function.declarator
        yield "{return_type} {name}({arguments});".format(
            return_type=build_type_expression(declarator.return_type),
            name=declarator.name,
            arguments=', '.join(build_parameter(p) for p in declarator.parameters)
        )

    def visit_callback_statement(self, statement):
        declarator = statement.callback.declarator
        yield "{return_type} {name}({arguments})".format(
            return_type=build_type_expression(declarator.return_type),
            name=declarator.name,
            arguments=', '.join(build_parameter(p) for p in declarator.parameters)
        ) + " {"
        if len(statement.interface.callback_declarations) > 0:
            yield indent(r"""printf("%s\n", "{name}");""".format(name=declarator.name))
        yield from indent_all(generate_block(statement.body))
        yield "}"

    def visit_main_statement(self, declaration):
        yield "int main() {"
        yield from indent_all(generate_block(declaration.body))
        yield "}"


class SkeletonGenerator(AbstractSupportGenerator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        main_file = open(os.path.join(self.dest_dir, "main.cpp"), "w")
        include_file = open(os.path.join(self.dest_dir, "main.h"), "w")
        write_to_file(self.generate_main_file(), main_file)

    def generate_main_file(self):
        yield "#include <cstdio>"
        generator = InterfaceItemGenerator()
        for statement in self.interface.body.statements:
            yield
            yield from accept_statement(statement, visitor=generator)
