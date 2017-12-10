import importlib
import os
import sys
from tempfile import TemporaryDirectory

import pkg_resources

from turingarena.common import ImmutableObject, install_with_setuptools
from turingarena.modules import module_to_python_package, prepare_module_dir, parse_module_name
from turingarena.protocol.model.exceptions import ProtocolError

PROTOCOL_QUALIFIER = "protocol"
ORIGINAL_SOURCE_FILENAME = "_original_source_filename.txt"


class ProtocolSource(ImmutableObject):
    __slots__ = [
        "filename",
        "text",
    ]

    def compile(self, **kwargs):
        # FIXME: make top-level
        from turingarena.protocol.model.model import ProtocolDefinition
        from turingarena.protocol.parser import parse_protocol

        ast = parse_protocol(self.text, **kwargs)
        return ProtocolDefinition.compile(ast=ast)

    def install(self, name):
        with TemporaryDirectory() as dest_dir:
            self._do_install(dest_dir, name)

    def _do_install(self, dest_dir, name):
        module_dir = prepare_module_dir(dest_dir, PROTOCOL_QUALIFIER, name)
        try:
            definition = self.compile(filename=self.filename)
        except ProtocolError as e:
            sys.exit(e.get_user_message())
        dest_source_filename = os.path.join(module_dir, "_source.tap")
        with open(dest_source_filename, "w") as f:
            f.write(self.text)
        dest_original_filename_filename = os.path.join(module_dir, ORIGINAL_SOURCE_FILENAME)
        with open(dest_original_filename_filename, "w") as f:
            f.write(self.filename)

        # FIXME: make top-level
        from turingarena.protocol.proxy.python import generate_proxy
        from turingarena.protocol.skeleton import generate_skeleton
        generate_proxy(module_dir, definition)
        generate_skeleton(definition, dest_dir=os.path.join(module_dir, "_skeletons"))
        package_name = module_to_python_package(PROTOCOL_QUALIFIER, name)
        levels = 5
        install_with_setuptools(
            dest_dir,
            name=package_name,
            packages=[package_name],
            package_data={
                # copy recursively up to levels
                package_name: ["/".join(["*"] * i) for i in range(1, levels)]
            },
            zip_safe=False,
        )


def install_protocol_from_source(source_dir, name):
    parts = parse_module_name(name)
    source_filename = os.path.join(source_dir, *parts[:-1], f"{parts[-1]}.tap")

    with open(source_filename) as f:
        source_text = f.read()

    source = ProtocolSource(filename=source_filename, text=source_text)
    source.install(name)


class ProtocolModule:
    __slots__ = ["name", "source"]

    def __init__(self, name):
        self.name = name

        module = module_to_python_package(PROTOCOL_QUALIFIER, self.name)
        source_text = pkg_resources.resource_string(module, "_source.tap").decode()
        source_original_filename = pkg_resources.resource_string(module, ORIGINAL_SOURCE_FILENAME).decode()

        self.source = ProtocolSource(
            text=source_text,
            filename=source_original_filename,
        )

    def load_definition(self):
        return self.source.compile()

    def load_interface_signature(self, interface_name):
        proxy_module = importlib.import_module(
            module_to_python_package(PROTOCOL_QUALIFIER, self.name) + "._proxy",
        )
        return getattr(proxy_module, interface_name)
