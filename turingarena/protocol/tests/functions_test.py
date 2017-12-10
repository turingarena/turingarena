from tempfile import TemporaryDirectory

import pkg_resources
import pytest

from turingarena.protocol.client import Implementation
from turingarena.sandbox.compile import sandbox_compile
from turingarena.setup import turingarena_setup


def test_functions_valid():
    with TemporaryDirectory() as temp_dir:
        protocol_name = "turingarena.protocol.tests.functions_valid"
        name = "functions_valid"

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

            phase = 0

            def cb_no_args():
                nonlocal phase
                assert phase == 0
                phase += 1

            def cb_args(a, b):
                nonlocal phase
                assert a == 2 and b == 3
                assert phase == 1
                phase += 1

            def cb_no_return_value(a):
                nonlocal phase
                assert a == 4
                assert phase == 2
                phase += 1

            def cb_return_value(a):
                nonlocal phase
                assert a == 5
                assert phase == 3
                phase += 1
                return 5

            y = p.invoke_callbacks(
                cb_no_args=cb_no_args,
                cb_args=cb_args,
                cb_no_return_value=cb_no_return_value,
                cb_return_value=cb_return_value,
            )
            assert phase == 4
            assert y == 5


def test_callable_return_type_not_scalar():
    protocol_names = [
        "turingarena.protocol.tests.function_return_type_not_scalar",
        "turingarena.protocol.tests.callback_return_type_not_scalar",
    ]
    for protocol_name in protocol_names:
        with pytest.raises(SystemExit) as excinfo:
            turingarena_setup(
                name=protocol_name,
                protocols=[protocol_name],
            )

        assert 'return type must be a scalar' in str(excinfo.value)


def test_callback_argument_not_scalar():
    protocol_name = "turingarena.protocol.tests.callback_argument_not_scalar"

    with pytest.raises(SystemExit) as excinfo:
        turingarena_setup(
            name=protocol_name,
            protocols=[protocol_name],
        )

    assert 'callback arguments must be scalars' in str(excinfo.value)


def test_interface_no_callbacks():
    protocol_name = "turingarena.protocol.tests.functions_valid"
    name = "interface_no_callbacks"
    with TemporaryDirectory() as temp_dir:
        sandbox_compile(
            dest_dir=temp_dir,
            source_filename=pkg_resources.resource_filename(
                __name__, f"{name}.cpp"
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
            assert p.test() == 1


def test_interface_one_callback():
    protocol_name = "turingarena.protocol.tests.functions_valid"
    name = "interface_one_callback"
    with TemporaryDirectory() as temp_dir:
        sandbox_compile(
            dest_dir=temp_dir,
            source_filename=pkg_resources.resource_filename(
                __name__, f"{name}.cpp"
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
            calls = []
            def cb():
                calls.append(cb)
            assert p.test(cb=cb) == 1
            assert calls == [cb, cb]


def test_interface_multiple_callbacks():
    protocol_name = "turingarena.protocol.tests.functions_valid"
    name = "interface_multiple_callbacks"
    with TemporaryDirectory() as temp_dir:
        sandbox_compile(
            dest_dir=temp_dir,
            source_filename=pkg_resources.resource_filename(
                __name__, f"{name}.cpp"
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
            calls = []
            def cb1():
                calls.append(cb1)
            def cb2():
                calls.append(cb2)
            assert p.test(cb1=cb1, cb2=cb2) == 1
            assert calls == [cb1, cb2, cb2, cb1]
