from tempfile import TemporaryDirectory

import pkg_resources
import pytest

from turingarena.protocol.model.exceptions import ProtocolError
from turingarena.protocol.proxy.python.engine import Implementation
from turingarena.sandbox.compile import sandbox_compile
from turingarena.setup import turingarena_setup


def test_functions_valid():
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


def test_function_return_type_not_scalar():
    protocol_name = "turingarena.protocol.tests.function_return_type_not_scalar"

    with pytest.raises(SystemExit) as excinfo:
        turingarena_setup(
            name=protocol_name,
            protocols=[protocol_name],
        )

    assert 'return type must be a scalar' in str(excinfo.value)
