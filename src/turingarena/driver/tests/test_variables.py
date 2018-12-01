from turingarena.driver.interface.diagnostics import ReferenceNotDefined, ReferenceAlreadyDefined, \
    ReferenceNotUsed
from turingarena.driver.tests.test_utils import assert_interface_error


def test_variable_not_declared():
    assert_interface_error("""
        main {
            write a;
        }
    """, ReferenceNotDefined(expression="'a'"))


def test_variable_not_declared_for():
    assert_interface_error("""
        procedure p(t[]);
        main {
            for i to a {
                read b[i];
            }
            call p(b);
        }
    """, ReferenceNotDefined(expression="'a'"))


def test_variable_reused():
    assert_interface_error("""
        main {
            read a;
            read a;
        }
    """, ReferenceAlreadyDefined(expression="'a'"))


def test_variable_not_written():
    assert_interface_error("""
        function f();
        
        main {
            call x = f();
        }
    """, ReferenceNotUsed(expression="x"))
