from __future__ import annotations

import subprocess
import os
import base64
from dataclasses import dataclass
from tempfile import NamedTemporaryFile


class Archive:
    """a tar archive"""
    tempfile: NamedTemporaryFile()

    @staticmethod
    def create(directory: str) -> Archive:
        """create an archive containing the files in directory"""
        self = Archive()
        self.tempfile = NamedTemporaryFile(prefix="turingarena-cli")
        subprocess.call(["/usr/bin/tar", "cf", self.tempfile.name, "-C", directory, "."])
        return self

    def extract(self, path: str):
        """extract the archive in the specified path"""
        os.makedirs(path, exist_ok=True)
        subprocess.call(["tar", "xf", self.tempfile.name, "-C", path])

    @property
    def base64(self) -> bytearray:
        """get the archive content as base64"""
        with open(self.tempfile.name, "rb") as f:
            return base64.standard_b64encode(f.read())

    def to_graphql(self) -> dict:
        return dict(base64=self.base64.decode("utf-8"))
