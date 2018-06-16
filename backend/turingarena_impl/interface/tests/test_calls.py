from turingarena_impl.interface.diagnostics import Diagnostic
from turingarena_impl.interface.tests.test_utils import assert_interface_error


def test_call_not_defined():
    assert_interface_error("""
        procedure f();
        main {
            call g();
        }
    """, Diagnostic.Messages.METHOD_NOT_DECLARED, "g")


def test_call_extra_arguments():
    assert_interface_error("""
        procedure f();
        main {
            call f(0, 1);
        }
    """, Diagnostic.Messages.CALL_WRONG_ARGS_NUMBER, "f", 0, 2)


def test_call_missing_arguments():
    assert_interface_error("""
        procedure f(a, b);
        main {
            call f(0);
        }
    """, Diagnostic.Messages.CALL_WRONG_ARGS_NUMBER, "f", 2, 1)


def   test_call_argument_wrong_type():
    assert_interface_error("""
        procedure f(a[]);
        main {
            call f(0);
        }
    """, Diagnostic.Messages.CALL_WRONG_ARGS_TYPE, "a", "f", "scalar[]", "scalar")


def test_call_missing_return_expression():
    assert_interface_error("""
        function f();
        main {
            call f();
        }
    """, Diagnostic.Messages.CALL_NO_RETURN_EXPRESSION, "f", "int")


def test_call_extra_return_expression():
    assert_interface_error("""
        procedure f();
        main {
            call a = f();
        }
    """, Diagnostic.Messages.METHOD_DOES_NOT_RETURN_VALUE, "f")
