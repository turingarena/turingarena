import os
from tempfile import TemporaryDirectory

from turingarena.tools.utils import write_to_file, indent_all
from turingarena.tools.install import install_with_setuptools


def generate_interface_proxy(signature):
    slots = ", ".join(f"'{v.name}'" for v in signature.variables.values())

    yield f"__slots__ = ['_engine', {slots}]"

    yield
    yield "def __init__(self, connection):"

    def engine_args():
        yield f"interface_signature={repr(signature)},"
        yield f"instance=self,"
        yield f"connection=connection,"

    def init_body():
        yield "self._engine = ProxyEngine("
        yield from indent_all(engine_args())
        yield ")"

    yield from indent_all(init_body())

    for name, f in signature.functions.items():
        yield
        parameters = [f"arg_{p.name}" for p in f.parameters]
        callbacks = [f"callback_{name}" for name in signature.callbacks]
        args = ", ".join(
            parameters +
            callbacks
        )
        yield f"def {name}(self, {args}):"

        def body():
            parameters_join = ", ".join(parameters)
            yield f"parameters = [{parameters_join}]"
            callbacks_join = "{" + ", ".join(f"'{name}': callback_{name}" for name in signature.callbacks) + "}"
            yield f"callbacks = {callbacks_join}"
            yield f"return self._engine.call('{name}', args=parameters, callbacks_impl=callbacks)"

        yield from indent_all(body())


def do_generate_proxy(protocol):
    yield "from collections import OrderedDict"
    yield "from turingarena.protocol.model.model import *"
    yield "from turingarena.protocol.model.type_expressions import *"
    yield "from turingarena.protocol.proxy.python.engine import ProxyEngine"
    yield
    for interface in protocol.body.scope.interfaces.values():
        yield f"class {interface.name}:"
        yield from indent_all(generate_interface_proxy(interface.signature))


def generate_proxy(protocol_id):
    package_name = f"turingarena_proxies.{protocol_id.name()}"
    protocol = protocol_id.load()

    with TemporaryDirectory() as dest_dir:
        namespace_dir = os.path.join(
            dest_dir,
            "turingarena_proxies",
        )
        package_dir = os.path.join(
            namespace_dir,
            str(protocol_id),
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
