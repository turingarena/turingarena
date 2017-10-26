import os

from turingarena.protocol.codegen.utils import write_to_file, indent_all
from turingarena.protocol.proxy.python.types import build_type, build_optional_type
from turingarena.protocol.visitor import accept_statement


class ProxyInterfaceGenerator:
    def __init__(self, interface):
        self.interface = interface

    def visit_var_statement(self, declaration):
        yield "interface_var({type}, [{names}]),".format(
            vars=", ".join(d.name for d in declaration.declarators),
            type=build_type(declaration.type),
            names=", ".join("'{}'".format(d.name) for d in declaration.declarators)
        )

    def visit_function_statement(self, statement):
        yield "interface_function({}),".format(build_signature(statement.declarator))

    def visit_callback_statement(self, statement):
        yield "interface_callback({}),".format(build_signature(statement.declarator))

    def visit_main_statement(self, statement):
        yield from []


def build_signature(signature):
    return "signature({name}, [{parameters}], {return_type})".format(
        fun=signature.name,
        name="'{}'".format(signature.name),
        parameters=", ".join(
            "arg({type}, '{name}')".format(
                type=build_type(p.type),
                name=p.declarator.name,
            )
            for p in signature.parameters
        ),
        return_type=build_optional_type(signature.return_type),
    )


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


def generate_proxy(protocol, *, dest_dir):
    package_name = protocol.package_name.replace(".", "_")

    qual_package_name = "turingarena_protocols." + package_name

    namespace_dir = os.path.join(
        dest_dir,
        "turingarena_protocols",
    )
    package_dir = os.path.join(
        namespace_dir,
        package_name,
    )

    os.makedirs(package_dir, exist_ok=True)

    module_path = os.path.join(
        package_dir,
        "__init__.py",
    )

    with open(module_path, "w") as module_file:
        write_to_file(do_generate_proxy(protocol), module_file)

    setup_py_path = os.path.join(
        dest_dir,
        "setup.py",
    )

    def generate_setup_py():
        yield "from setuptools import setup"
        yield
        yield "setup("
        yield "    name='{}',".format(qual_package_name)
        yield "    namespace_packages=['turingarena_protocols'],"
        yield "    packages=['turingarena_protocols', '{}'],".format(qual_package_name)
        yield ")"

    with open(setup_py_path, "w") as setup_py_file:
        write_to_file(generate_setup_py(), setup_py_file)
