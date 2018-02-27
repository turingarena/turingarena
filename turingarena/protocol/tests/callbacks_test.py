import pytest

from turingarena.protocol.exceptions import ProtocolError
from turingarena.protocol.model.model import InterfaceDefinition
from turingarena.test_utils import callback_mock, define_many


def test_callback_no_arguments_cpp():
    for algo in define_many(
            interface_text="""
                callback callback_no_arguments() {}
                function test();
                main {
                    call test();
                }
            """,
            sources={
                'c++': """
                    void callback_no_arguments();
                    void test() {
                        callback_no_arguments();
                        callback_no_arguments();
                    }
                """,
                'python': """if True:
                    from __main__ import callback_no_arguments
                    
                    def test():
                        callback_no_arguments()
                        callback_no_arguments()
                """,
            }
    ):
        with algo.run() as (process, p):
            calls = []
            callback_no_arguments = callback_mock(calls)
            p.test(callback_no_arguments=callback_no_arguments)

            assert calls == [
                (callback_no_arguments, ()),
                (callback_no_arguments, ()),
            ]


def test_callback_with_arguments():
    for algo in define_many(
            interface_text="""
                callback callback_with_arguments(int a, int b) {
                    output a, b;
                }
                function test();
                main {
                    call test();
                }
            """,
            sources={
                'c++': """
                    void callback_with_arguments(int a, int b);
                    void test() {
                        callback_with_arguments(1, 2);
                        callback_with_arguments(3, 4);
                    }
                """,
                'python': """if True:
                    from __main__ import callback_with_arguments
                    def test():
                        callback_with_arguments(1, 2)
                        callback_with_arguments(3, 4)
                """,
            },
    ):
        with algo.run() as (process, p):
            calls = []
            callback_with_arguments = callback_mock(calls)
            p.test(callback_with_arguments=callback_with_arguments)

            assert calls == [
                (callback_with_arguments, (1, 2)),
                (callback_with_arguments, (3, 4)),
            ]


def test_callback_return_value():
    for algo in define_many(
            interface_text="""
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
            """,
            sources={
                'c++': """
                    #include <cassert>
                    int callback_return_value(int a);
                    void test() {
                        assert(callback_return_value(1) == 2);
                        assert(callback_return_value(3) == 4);
                    }
                """,
                'python': """if True:
                    from __main__ import callback_return_value
                    def test():
                        assert callback_return_value(1) == 2
                        assert callback_return_value(3) == 4
                """
            }
    ):
        with algo.run() as (process, p):
            calls = []
            callback_return_value = callback_mock(calls, [2, 4])
            p.test(callback_return_value=callback_return_value)

            assert calls == [
                (callback_return_value, (1,)),
                (callback_return_value, (3,)),
            ]


def test_callback_return_type_not_scalar():
    protocol_text = """
        callback callback_return_type_not_scalar() -> int[] {}
        main {}
    """
    with pytest.raises(ProtocolError) as excinfo:
        InterfaceDefinition.compile(protocol_text)
    assert 'return type must be a scalar' in excinfo.value.get_user_message()


def test_callback_argument_not_scalar():
    protocol_text = """
        callback callback_argument_not_scalar(int ok, int[] wrong) {}
        main {}
    """
    with pytest.raises(ProtocolError) as excinfo:
        InterfaceDefinition.compile(protocol_text)
    assert 'callback arguments must be scalars' in excinfo.value.get_user_message()
