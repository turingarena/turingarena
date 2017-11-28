import subprocess
from tempfile import TemporaryDirectory
from unittest.case import TestCase

import pkg_resources

from turingarena.sandbox.compile import sandbox_compile


class FunctionsValid(TestCase):
    def test_compile(self):
        with TemporaryDirectory() as temp_dir:
            sandbox_compile(
                dest_dir=temp_dir,
                source_filename=pkg_resources.resource_filename(
                    "turingarena.tests", f"functions_valid.cpp"
                ),
                protocol_name="turingarena.tests.functions_valid",
                interface_name="functions_valid",
                algorithm_name="functions_valid",
                check=True,
            )
