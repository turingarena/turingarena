from turingarena.interface.tests.test_utils import assert_interface_error
from turingarena.interface.exceptions import Diagnostic

def test_call_not_defined():
    assert_interface_error("""
        function f();
        main {
            /*!*/ call g(); /*!*/
        }
    """, Diagnostic.Messages.FUNCTION_NOT_DECLARED, "g")


def test_call_extra_arguments():
    assert_interface_error("""
        function f();
        main {
            /*!*/ call f(0, 1); /*!*/
        }
    """, Diagnostic.Messages.CALL_WRONG_ARGS_NUMBER, "f", 0, 2)


def test_call_missing_arguments():
    assert_interface_error("""
        function f(int a, int b);
        main {
            /*!*/ call f(0); /*!*/
        }
    """, Diagnostic.Messages.CALL_WRONG_ARGS_NUMBER, "f", 2, 1)


def test_call_argument_wrong_type():
    assert_interface_error("""
        function f(int[] a);
        main {
            call f(/*!*/ 0 /*!*/);
        }
    """, Diagnostic.Messages.CALL_WRONG_ARGS_TYPE, "a", "f", "int[]", "int")


def test_call_missing_return_expression():
    assert_interface_error("""
        function f() -> int;
        main {
            /*!*/ call f(); /*!*/
        }
    """, Diagnostic.Messages.CALL_NO_RETURN_EXPRESSION, "f", "int")


def test_call_extra_return_expression():
    assert_interface_error("""
        function f();
        main {
            var int a;
            call f() -> /*!*/ a /*!*/;
        }
    """, Diagnostic.Messages.FUNCTION_DOES_NOT_RETURN_VALUE, "f")


def test_call_return_expression_wrong_type():
    assert_interface_error("""
        function f() -> int;
        main {
            var int[] a;
            call f() -> /*!*/ a /*!*/;
        }
    """, Diagnostic.Messages.CALL_WRONG_RETURN_EXPRESSION, "f", "int", "int[]")

