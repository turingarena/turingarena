from turingarena_impl.interface.exceptions import Diagnostic
from .test_utils import assert_interface_error, assert_no_interface_errors


def test_array_alloc():
    assert_interface_error("""
        main {
            read A[5];
            write A[5];
        }
    """, Diagnostic.Messages.ARRAY_INDEX_NOT_VALID, "5")


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


def test_array_basic_error():
    assert_interface_error("""
        procedure f(A[][]);
        procedure i(i);
    
        main {
            read s; 
            call i(s);
            for i to s {
                read k;
                call i(k);
                for j to k {
                    read A[i][k];
                } 
            }
            
            call f(A);
        }
    """, Diagnostic.Messages.ARRAY_INDEX_NOT_VALID, "k")


def test_array_wrong_order():
    assert_interface_error("""
        procedure f(A[][]);
        procedure i(i);

        main {
            read s; 
            call i(s);
            for i to s {
                read k;
                call i(k);
                for j to k {
                    read A[j][i];
                } 
            }
            
            call f(A);
        }
    """, Diagnostic.Messages.ARRAY_INDEX_WRONG_ORDER, "A")
