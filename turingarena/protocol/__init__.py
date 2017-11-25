import importlib
import os
import re

import pkg_resources

from turingarena.common import TupleLikeObject
from turingarena.protocol.model.model import Protocol
from turingarena.protocol.parser import parse_protocol

part_regex = re.compile("^[a-z][a-z_]*$")


class ProtocolIdentifier(TupleLikeObject):
    __slots__ = ["parts"]

    def __init__(self, name):
        parts = name.split(".")
        assert len(parts) >= 1
        assert all(
            part_regex.fullmatch(part) is not None
            for part in parts
        )
        super().__init__(parts=parts)

    def to_command(self):
        return (
            f"turingarena protocol --name {self.name()}"
        )

    def source_dir(self):
        dirs = self.parts[:-2]
        if dirs:
            return os.path.join(*dirs)
        else:
            return "."

    def source_filename(self):
        return f"{self.parts[-1]}.tap"

    def source_path(self):
        return os.path.join(self.source_dir(), self.source_filename())

    def full_dir(self):
        return os.path.join(*self.parts)

    def name(self):
        return ".".join(self.parts)

    def python_package(self):
        return "turingarena_protocols." + self.name()

    def python_package_dir(self):
        return os.path.join("turingarena_protocols", self.full_dir())

    def load(self):
        protocol_def = pkg_resources.resource_string(self.python_package(), "__init__.tap")
        ast = parse_protocol(protocol_def.decode())
        return Protocol.compile(ast=ast, id=self)

    def load_signature(self, interface_name):
        proxy_module = importlib.import_module(f"turingarena_proxies.{self.name()}")
        return getattr(proxy_module, interface_name)

    def __str__(self):
        return self.name()
