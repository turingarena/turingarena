from unittest.case import TestCase

import pkg_resources

from turingarena.sandbox.compile import sandbox_compile


class FunctionsValid(TestCase):
    def test_compile_all(self):
        for interface_name in [
            "function_no_args",
            "function_args",
            "function_no_return_value",
            "function_return_value",
        ]:
            sandbox_compile(
                source_filename=pkg_resources.resource_filename(
                    "turingarena.tests", f"{interface_name}.cpp"
                ),
                protocol_name="turingarena.tests.functions_valid",
                interface_name=interface_name,
                algorithm_name=interface_name,
                check=True,
            )
