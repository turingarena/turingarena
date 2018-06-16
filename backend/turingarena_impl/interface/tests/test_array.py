from turingarena_impl.interface.diagnostics import Diagnostic
from turingarena_impl.interface.tests.test_utils import assert_interface_diagnostics
from .test_utils import assert_no_interface_errors


def test_array_alloc():
    assert_interface_diagnostics("""
        procedure p(a[]);
        main {
            read a[5];
            call p(a);
            checkpoint;
        }
    """, [Diagnostic.build_message(Diagnostic.Messages.UNEXPECTED_ARRAY_INDEX)])


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
