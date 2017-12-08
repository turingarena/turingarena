from tempfile import TemporaryDirectory

import pkg_resources

from turingarena.protocol.proxy.python.engine import Implementation
from turingarena.sandbox.compile import sandbox_compile
from turingarena.setup import turingarena_setup


def test_compile():
    with TemporaryDirectory() as temp_dir:
        protocol_name = "turingarena.protocol.tests.functions_valid"
        name = "functions_valid"

        turingarena_setup(
            name=protocol_name,
            protocols=[protocol_name],
        )

        sandbox_compile(
            dest_dir=temp_dir,
            source_filename=pkg_resources.resource_filename(
                __name__, f"functions_valid.cpp"
            ),
            protocol_name=protocol_name,
            interface_name=name,
            algorithm_name=name,
            check=True,
        )

        impl = Implementation(
            work_dir=temp_dir,
            protocol_name=protocol_name,
            interface_name=name,
            algorithm_name=name,
        )
        with impl.run() as p:
            p.no_args()
            p.args(0, 0)
            p.no_return_value(0)
            x = p.return_value(0)
        assert x == 0
