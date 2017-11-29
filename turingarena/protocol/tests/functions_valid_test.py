from tempfile import TemporaryDirectory

import pkg_resources

from turingarena.sandbox.compile import sandbox_compile


def test_compile():
    with TemporaryDirectory() as temp_dir:
        sandbox_compile(
            dest_dir=temp_dir,
            source_filename=pkg_resources.resource_filename(
                __name__, f"functions_valid.cpp"
            ),
            protocol_name="turingarena.protocol.tests.functions_valid",
            interface_name="functions_valid",
            algorithm_name="functions_valid",
            check=True,
        )
