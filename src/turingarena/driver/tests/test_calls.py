from turingarena.driver.interface.diagnostics import MethodNotDeclared, InvalidNumberOfArguments, \
    InvalidArgument, IgnoredReturnValue, NoReturnValue
from turingarena.driver.tests.test_utils import assert_interface_error


def test_call_not_defined():
    assert_interface_error("""
        procedure f();
        main {
            call g();
        }
    """, MethodNotDeclared(name="g"))


def test_call_extra_arguments():
    assert_interface_error("""
        procedure f();
        main {
            call f(0, 1);
        }
    """, InvalidNumberOfArguments(name="f", n_parameters=0, n_arguments=2))


def test_call_missing_arguments():
    assert_interface_error("""
        procedure f(a, b);
        main {
            call f(0);
        }
    """, InvalidNumberOfArguments(name="f", n_parameters=2, n_arguments=1))


def test_call_argument_wrong_type():
    assert_interface_error("""
        procedure f(a[]);
        main {
            call f(0);
        }
    """, InvalidArgument(name="f", parameter="a", dimensions=1, argument="'0'"))


def test_call_missing_return_expression():
    assert_interface_error("""
        function f();
        main {
            call f();
        }
    """, IgnoredReturnValue(name="f"))


def test_call_extra_return_expression():
    assert_interface_error("""
        procedure f();
        main {
            call a = f();
        }
    """, NoReturnValue(name="f"))
