import os
from tempfile import TemporaryDirectory

from gevent import subprocess

from turingarena.protocol.codegen.utils import write_to_file


def do_generate_proxy(protocol):
    yield "from collections import OrderedDict"
    yield "from turingarena.protocol.model.model import *"
    yield "from turingarena.protocol.model.type_expressions import *"
    yield
    for interface in protocol.body.scope.interfaces.values():
        yield f"{interface.name} = {repr(interface.signature)}"


def generate_proxy(protocol_id):
    qual_package_name = protocol_id.python_package()

    def generate_setup_py():
        yield "from setuptools import setup"
        yield
        yield f"setup("
        yield f"    name='{qual_package_name}',"
        yield f"    packages=['turingarena_protocols', '{qual_package_name}'],"
        yield f")"

    with TemporaryDirectory() as dest_dir:
        namespace_dir = os.path.join(
            dest_dir,
            "turingarena_protocols",
        )
        package_dir = os.path.join(
            namespace_dir,
            str(protocol_id),
        )

        os.makedirs(package_dir, exist_ok=True)

        with open(os.path.join(package_dir, "__init__.py"), "w") as module_file:
            write_to_file(do_generate_proxy(protocol), module_file)

        setup_py_path = os.path.join(
            dest_dir,
            "setup.py",
        )

        with open(setup_py_path, "w") as setup_py_file:
            write_to_file(generate_setup_py(), setup_py_file)

        subprocess.run(
            ["python", "setup.py", "install"],
            chdir=dest_dir,
        )


def build_type(type_expression):
    return repr(type_expression)


def build_optional_type(type_expression):
    if type_expression is None:
        return "None"
    return build_type(type_expression)
