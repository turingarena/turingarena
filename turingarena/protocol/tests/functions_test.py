import pytest

from turingarena.protocol.exceptions import ProtocolError
from turingarena.protocol.module import ProtocolSource
from turingarena.protocol.tests.util import cpp_implementation, python_implementation


def test_function_no_arguments_cpp():
    with cpp_implementation(
            protocol_text="""
                interface function_no_arguments {
                    function function_no_arguments();
                    main {
                        call function_no_arguments();
                    }
                }
            """,
            source_text="""
                void function_no_arguments() {
                }
            """,
            interface_name="function_no_arguments",
    ) as impl:
        with impl.run() as (process, p):
            p.function_no_arguments()


def test_function_no_arguments_python():
    with python_implementation(
            protocol_text="""
                interface function_no_arguments {
                    function function_no_arguments();
                    main {
                        call function_no_arguments();
                    }
                }
            """,
            source_text="""if True:
                def function_no_arguments():
                    pass
            """,
            interface_name="function_no_arguments",
    ) as impl:
        with impl.run() as (process, p):
            p.function_no_arguments()


def test_function_with_arguments_cpp():
    with cpp_implementation(
            protocol_text="""
                interface function_with_arguments {
                    function function_with_arguments(int a, int b);
                    main {
                        var int a, b;
                        input a, b;
                        call function_with_arguments(a, b);
                    }
                }
            """,
            source_text="""
                #include <cassert>
                void function_with_arguments(int a, int b) {
                    assert(a == 1 && b == 2);
                }
            """,
            interface_name="function_with_arguments",
    ) as impl:
        with impl.run() as (process, p):
            p.function_with_arguments(1, 2)


def test_function_with_arguments_python():
    with python_implementation(
            protocol_text="""
                interface function_with_arguments {
                    function function_with_arguments(int a, int b);
                    main {
                        var int a, b;
                        input a, b;
                        call function_with_arguments(a, b);
                    }
                }
            """,
            source_text="""if True:
                def function_with_arguments(a,b):
                    assert a == 1 and b == 2
            """,
            interface_name="function_with_arguments",
    ) as impl:
        with impl.run() as (process, p):
            p.function_with_arguments(1, 2)


def test_function_return_value_cpp():
    with cpp_implementation(
            protocol_text="""
                interface function_return_value {
                    function function_return_value(int a) -> int;
                    main {
                        var int a, b;
                        input a;
                        call function_return_value(a) -> b;
                        output b;
                    }
                }
            """,
            source_text="""
                #include <cassert>
                int function_return_value(int a) {
                    assert(a == 1);
                    return 2;
                }
            """,
            interface_name="function_return_value",
    ) as impl:
        with impl.run() as (process, p):
            assert p.function_return_value(1) == 2


def test_function_return_value_python():
    with python_implementation(
            protocol_text="""
                interface function_return_value {
                    function function_return_value(int a) -> int;
                    main {
                        var int a, b;
                        input a;
                        call function_return_value(a) -> b;
                        output b;
                    }
                }
            """,
            source_text="""if True:
                def function_return_value(a):
                    assert a == 1
                    return 2
            """,
            interface_name="function_return_value",
    ) as impl:
        with impl.run() as (process, p):
            assert p.function_return_value(1) == 2


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
    assert 'return type must be a scalar' in excinfo.value.get_user_message()
