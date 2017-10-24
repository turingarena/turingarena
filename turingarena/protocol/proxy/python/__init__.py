import os

from turingarena.protocol.codegen.utils import write_to_file, indent_all
from turingarena.protocol.proxy.python.types import build_type_expression, build_optional_type_expression
from turingarena.protocol.visitor import accept_statement


class ProxyInterfaceGenerator:
    def __init__(self, interface):
        self.interface = interface

    def visit_var_statement(self, declaration):
        yield "interface_var({type}, [{names}]),".format(
            vars=", ".join(d.name for d in declaration.declarators),
            type=build_type_expression(declaration.type),
            names=", ".join("'{}'".format(d.name) for d in declaration.declarators)
        )

    def visit_function_statement(self, statement):
        name = statement.declarator.name
        yield "interface_function({name}, [{parameters}], {return_type}),".format(
            fun=name,
            name="'{}'".format(name),
            parameters=", ".join(
                "arg({type}, '{name}')".format(
                    type=build_type_expression(p.type),
                    name=p.declarator.name,
                )
                for p in statement.parameters
            ),
            return_type=build_optional_type_expression(statement.return_type),
        )

    def visit_callback_statement(self, declaration):
        yield from []

    def visit_main_statement(self, declaration):
        yield from []


def do_generate_proxy(protocol):
    yield "from __future__ import print_function"
    yield "from turingarena.protocol.proxy.python.library import *"
    yield
    for interface in protocol.interfaces:
        yield "{} = ".format(interface.name) + "["
        yield from indent_all(generate_interface_proxy(interface))
        yield "]".format(interface.name)


def generate_interface_proxy(interface):
    for statement in interface.statements:
        yield from accept_statement(statement, visitor=ProxyInterfaceGenerator(interface))


def generate_proxy(protocol, *, proxy_dir):
    module_path = os.path.join(
        proxy_dir,
        "proxy.py"
    )

    module_file = open(module_path, "w")
    write_to_file(do_generate_proxy(protocol), module_file)
