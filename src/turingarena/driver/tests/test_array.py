from turingarena.driver.interface.diagnostics import InvalidReference
from turingarena.driver.tests.test_utils import assert_interface_diagnostics
from .test_utils import assert_no_interface_errors


def test_array_alloc():
    assert_interface_diagnostics("""
        procedure p(a[]);
        main {
            read a[5];
            call p(a);
            checkpoint;
        }
    """, [InvalidReference(expression="'a[5]'")])


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
