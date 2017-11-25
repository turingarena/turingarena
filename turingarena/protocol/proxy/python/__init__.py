import os
from tempfile import TemporaryDirectory

from turingarena.protocol.packaging import load_protocol
from turingarena.tools.utils import write_to_file, indent_all
from turingarena.tools.install import install_with_setuptools


def do_generate_proxy(protocol):
    yield "from collections import OrderedDict"
    yield "from turingarena.protocol.model.model import *"
    yield "from turingarena.protocol.model.type_expressions import *"
    yield
    for interface in protocol.body.scope.interfaces.values():
        yield f"{interface.name} = {repr(interface.signature)}"


def generate_proxy(protocol_name):
    package_name = f"turingarena_proxies.{protocol_name}"
    protocol = load_protocol(protocol_name)

    with TemporaryDirectory() as dest_dir:
        namespace_dir = os.path.join(
            dest_dir,
            "turingarena_proxies",
        )
        package_dir = os.path.join(
            namespace_dir,
            protocol_name,
        )

        os.makedirs(package_dir)

        with open(os.path.join(package_dir, "__init__.py"), "w") as module_file:
            write_to_file(do_generate_proxy(protocol), module_file)

        install_with_setuptools(
            dest_dir,
            name=package_name,
            packages=[package_name],
            zip_safe=False,
        )


def build_type(type_expression):
    return repr(type_expression)


def build_optional_type(type_expression):
    if type_expression is None:
        return "None"
    return build_type(type_expression)
