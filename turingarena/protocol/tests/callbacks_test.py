import pytest

from turingarena.protocol.exceptions import ProtocolError
from turingarena.protocol.module import ProtocolSource
from turingarena.protocol.tests.util import cpp_implementation, callback_mock


def test_callback_no_arguments():
    with cpp_implementation(
            protocol_text="""
                interface callback_no_arguments {
                    callback callback_no_arguments() {}
                    function test();
                    main {
                        call test();
                    }
                }
            """,
            source_text="""
                void callback_no_arguments();
                void test() {
                    callback_no_arguments();
                    callback_no_arguments();
                }
            """,
            interface_name="callback_no_arguments",
    ) as impl:
        with impl.run() as (process, p):
            calls = []
            callback_no_arguments = callback_mock(calls)
            p.test(callback_no_arguments=callback_no_arguments)

            assert calls == [
                (callback_no_arguments, ()),
                (callback_no_arguments, ()),
            ]


def test_callback_with_arguments():
    with cpp_implementation(
            protocol_text="""
                interface callback_with_arguments {
                    callback callback_with_arguments(int a, int b) {
                        output a, b;
                    }
                    function test();
                    main {
                        call test();
                    }
                }
            """,
            source_text="""
                void callback_with_arguments(int a, int b);
                void test() {
                    callback_with_arguments(1, 2);
                    callback_with_arguments(3, 4);
                }
            """,
            interface_name="callback_with_arguments",
    ) as impl:
        with impl.run() as (process, p):
            calls = []
            callback_with_arguments = callback_mock(calls)
            p.test(callback_with_arguments=callback_with_arguments)

            assert calls == [
                (callback_with_arguments, (1, 2)),
                (callback_with_arguments, (3, 4)),
            ]


def test_callback_return_value():
    with cpp_implementation(
            protocol_text="""
                interface callback_return_value {
                    callback callback_return_value(int a) -> int {
                        output a;
                        flush;
                        var int b;
                        input b;
                        return b;
                    }
                    function test();
                    main {
                        call test();
                    }
                }
            """,
            source_text="""
                #include <cassert>
                int callback_return_value(int a);
                void test() {
                    assert(callback_return_value(1) == 2);
                    assert(callback_return_value(3) == 4);
                }
            """,
            interface_name="callback_return_value",
    ) as impl:
        with impl.run() as (process, p):
            calls = []
            callback_return_value = callback_mock(calls, [2, 4])
            p.test(callback_return_value=callback_return_value)

            assert calls == [
                (callback_return_value, (1,)),
                (callback_return_value, (3,)),
            ]


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
    assert 'return type must be a scalar' in excinfo.value.get_user_message()


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

    assert 'callback arguments must be scalars' in excinfo.value.get_user_message()
