import os
import re

from turingarena.common import TupleLikeObject

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

    def name(self):
        return ".".join(self.parts)

    def python_package(self):
        return "turingarena_protocols." + self.name()

    def python_package_dir(self):
        return os.path.join("turingarena_protocols", *self.parts)

    def __str__(self):
        return self.name()
