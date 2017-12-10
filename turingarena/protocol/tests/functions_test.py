import pytest

from turingarena.protocol.model.exceptions import ProtocolError
from turingarena.protocol.module import ProtocolSource
from turingarena.protocol.tests.util import cpp_implementation


def test_functions_valid():
    protocol_text = """
        interface functions_valid {
            function no_args();
            function args(int a, int b);
            function no_return_value(int a);
            function return_value(int a) -> int;
        
            callback cb_no_args() {}
            callback cb_args(int a, int b) {
                output a, b;
            }
            callback cb_no_return_value(int a) {
                output a;
            }
        
            callback cb_return_value(int a) -> int {
                output a;
                flush;
                var int ans;
                input ans;
                return ans;
            }
        
            function invoke_callbacks() -> int;
        
            main {
                call no_args();
                call args(0, 0);
                call no_return_value(0);
                var int x;
                call return_value(0) -> x;
                output x;
                var int y;
                call invoke_callbacks() -> y;
                output y;
            }
        }
    """

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
            protocol_text=protocol_text,
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
    protocol_text = """
        interface interface_no_callbacks {
            function test() -> int;
            main {
                var int o;
                call test() -> o;
                output o;
            }
        }
    """

    source_text = """
        int test() {
            return 1;
        }
    """
    with cpp_implementation(
            protocol_text=protocol_text,
            source_text=source_text,
            protocol_name="turingarena.protocol.tests.interface_no_callbacks",
            interface_name="interface_no_callbacks",
    ) as impl:
        with impl.run() as p:
            assert p.test() == 1


def test_interface_one_callback():
    protocol_text = """
        interface interface_one_callback {
            callback cb() {}
            function test() -> int;
            main {
                var int o;
                call test() -> o;
                output o;
            }
        }
    """

    source_text = """
        void cb();
        
        int test() {
            cb();
            cb();
            return 1;
        }
    """
    with cpp_implementation(
            protocol_text=protocol_text,
            source_text=source_text,
            protocol_name="turingarena.protocol.tests.interface_one_callback",
            interface_name="interface_one_callback",
    ) as impl:
        with impl.run() as p:
            calls = []

            def cb():
                calls.append(cb)

            assert p.test(cb=cb) == 1
            assert calls == [cb, cb]


def test_interface_multiple_callbacks():
    protocol_text = """
        interface interface_multiple_callbacks {
            callback cb1() {}
            callback cb2() {}
            function test() -> int;
            main {
                var int o;
                call test() -> o;
                output o;
            }
        }
    """

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
            protocol_text=protocol_text,
            source_text=source_text,
            protocol_name="turingarena.protocol.tests.interface_multiple_callbacks",
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


def test_function_return_type_not_scalar():
    protocol_text = """
        interface function_return_type_not_scalar {
            function function_return_type_not_scalar() -> int[];
            main {}
        }
    """
    source = ProtocolSource(
        text=protocol_text,
        filename="<none>",
    )

    with pytest.raises(ProtocolError) as excinfo:
        source.compile()
    assert 'return type must be a scalar' in str(excinfo.value.get_user_message())


def test_callback_return_type_not_scalar():
    protocol_text = """
        interface callback_return_type_not_scalar {
            callback callback_return_type_not_scalar() -> int[] {}
            main {}
        }
    """
    source = ProtocolSource(
        text=protocol_text,
        filename="<none>",
    )

    with pytest.raises(ProtocolError) as excinfo:
        source.compile()
    assert 'return type must be a scalar' in str(excinfo.value.get_user_message())


def test_callback_argument_not_scalar():
    protocol_text = """
        interface callback_argument_not_scalar {
            callback callback_argument_not_scalar(int ok, int[] wrong) {}
            main {}
        }
    """
    source = ProtocolSource(
        text=protocol_text,
        filename="<none>",
    )

    with pytest.raises(ProtocolError) as excinfo:
        source.compile()

    assert 'callback arguments must be scalars' in str(excinfo.value)
