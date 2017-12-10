import pytest

from turingarena.protocol.tests.util import cpp_implementation
from turingarena.setup import turingarena_setup


def test_functions_valid():
    source_text = """
        void args(int a, int b) {
        }
        
        void no_args() {
        }
        
        void no_return_value(int a) {
        }
        
        int return_value(int a) {
            return 0;
        }
        
        void cb_no_args();
        void cb_args(int a, int b);
        void cb_no_return_value(int a);
        int cb_return_value(int a);
        
        int invoke_callbacks() {
            cb_no_args();
            cb_args(2, 3);
            cb_no_return_value(4);
            return cb_return_value(5);
        }
    """

    with cpp_implementation(
            source_text=source_text,
            protocol_name="turingarena.protocol.tests.functions_valid",
            interface_name="functions_valid",
    ) as impl:
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


def test_interface_no_callbacks():
    source_text = """
        int test() {
            return 1;
        }
    """
    with cpp_implementation(
            source_text=source_text,
            protocol_name="turingarena.protocol.tests.functions_valid",
            interface_name="interface_no_callbacks",
    ) as impl:
        with impl.run() as p:
            assert p.test() == 1


def test_interface_one_callback():
    source_text = """
        void cb();
        
        int test() {
            cb();
            cb();
            return 1;
        }
    """
    with cpp_implementation(
            source_text=source_text,
            protocol_name="turingarena.protocol.tests.functions_valid",
            interface_name="interface_one_callback",
    ) as impl:
        with impl.run() as p:
            calls = []

            def cb():
                calls.append(cb)

            assert p.test(cb=cb) == 1
            assert calls == [cb, cb]


def test_interface_multiple_callbacks():
    source_text = """
        void cb1();
        void cb2();
        
        int test() {
            cb1();
            cb2();
            cb2();
            cb1();
            return 1;
        }
    """
    with cpp_implementation(
            source_text=source_text,
            protocol_name="turingarena.protocol.tests.functions_valid",
            interface_name="interface_multiple_callbacks",
    ) as impl:
        with impl.run() as p:
            calls = []

            def cb1():
                calls.append(cb1)

            def cb2():
                calls.append(cb2)

            assert p.test(cb1=cb1, cb2=cb2) == 1
            assert calls == [cb1, cb2, cb2, cb1]


def test_callable_return_type_not_scalar():
    protocol_names = [
        "turingarena.protocol.tests.function_return_type_not_scalar",
        "turingarena.protocol.tests.callback_return_type_not_scalar",
    ]
    for protocol_name in protocol_names:
        with pytest.raises(SystemExit) as excinfo:
            turingarena_setup(
                protocols=[protocol_name],
            )

        assert 'return type must be a scalar' in str(excinfo.value)


def test_callback_argument_not_scalar():
    protocol_name = "turingarena.protocol.tests.callback_argument_not_scalar"

    with pytest.raises(SystemExit) as excinfo:
        turingarena_setup(
            protocols=[protocol_name],
        )

    assert 'callback arguments must be scalars' in str(excinfo.value)
