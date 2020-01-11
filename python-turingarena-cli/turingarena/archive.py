from __future__ import annotations

import subprocess
import os
import base64

from tempfile import NamedTemporaryFile


class Archive:
    tempfile: NamedTemporaryFile()

    @staticmethod
    def create(directory: str) -> Archive:
        self = Archive()
        self.tempfile = NamedTemporaryFile(prefix="turingarena-cli")
        subprocess.call(["tar", "cf", self.tempfile.name, "-C", directory, "."])
        return self

    def extract(self, path: str):
        os.makedirs(path, exist_ok=True)
        subprocess.call(["tar", "xf", self.tempfile.name, "-C", path])

    @property
    def base64(self) -> bytearray:
        with open(self.tempfile.name, "rb") as f:
            return base64.standard_b64encode(f.read())

    def to_graphql(self) -> dict:
        return dict(base64=self.base64.decode("utf-8"))
