from turingarena.driver.interface.diagnostics import InvalidReference, UnexpectedIndexForReference, \
    InvalidIndexForReference
from turingarena.driver.tests.test_utils import assert_interface_diagnostics
from .test_utils import assert_no_interface_errors


def test_unexpected_index():
    assert_interface_diagnostics("""
        procedure p(x);
        main {
            read a[5];
            call p(a[5]);
            checkpoint;
        }
    """, [UnexpectedIndexForReference(expression="'a[5]'")])


def test_invalid_index():
    assert_interface_diagnostics("""
        procedure p(x);
        main {
            for i to 2 {
                for j to 2 {
                    read a[i];
                    call p(a[i]);
                }
            }
            checkpoint;
        }
    """, [InvalidIndexForReference(expression="'a[i]'", index="j")])


def test_array_basic():
    assert_no_interface_errors("""
        procedure f(A[][]);
    
        main {
            for i to 10 {
                for j to 10 {
                    read A[i][j];
                } 
            }
            call f(A);
        }
    """)
