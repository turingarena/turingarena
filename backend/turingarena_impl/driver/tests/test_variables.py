from turingarena_impl.driver.interface.diagnostics import Diagnostic
from turingarena_impl.driver.tests.test_utils import assert_interface_error


def test_variable_not_declared():
    assert_interface_error("""
        main {
            write a;
        }
    """, Diagnostic.Messages.VARIABLE_NOT_DECLARED, "a")


def test_variable_not_declared_for():
    assert_interface_error("""
        procedure p(t[]);
        main {
            for i to a {
                read b[i];
            }
            call p(b);
        }
    """, Diagnostic.Messages.VARIABLE_NOT_DECLARED, "a")


def test_variable_reused():
    assert_interface_error("""
        main {
            read a;
            read a;
        }
    """, Diagnostic.Messages.VARIABLE_REUSED, "a")


def test_variable_not_written():
    assert_interface_error("""
        function f();
        
        main {
            call x = f();
        }
    """, Diagnostic.Messages.VARIABLE_NOT_WRITTEN, "x")
