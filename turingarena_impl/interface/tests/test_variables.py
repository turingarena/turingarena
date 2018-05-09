from turingarena_impl.interface.exceptions import Diagnostic
from turingarena_impl.interface.tests.test_utils import assert_no_interface_errors, assert_interface_error


def test_variable_not_declared():
    assert_interface_error("""
        main {
            write a;
        }
    """, Diagnostic.Messages.VARIABLE_NOT_DECLARED, "a")


def test_variable_reused():
    assert_interface_error("""
        main {
            read a;
            read a;
        }
    """, Diagnostic.Messages.VARIABLE_REUSED, "a")
