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
        void f(int array[][]);
    
        main {
            for i to 10 {
                for j to 10 {
                    read A[i][j];
                } 
            }
            f(A);
        }
    """)


def test_array_basic_error():
    assert_interface_error("""
        main {
            var int[][] A;
            var int s;
            read s; 
            alloc A : s;
            for (i : s) {
                var int k;
                read k;
                alloc A[i] : k;
                for (j : k) {
                    read A[i][k];
                } 
            }
        }
    """, Diagnostic.Messages.ARRAY_INDEX_NOT_VALID, "k")


def test_array_wrong_order():
    assert_interface_error("""
        main {
            var int[][] A;
            var int s;
            read s; 
            alloc A : s;
            for (i : s) {
                var int k;
                read k;
                alloc A[i] : k;
                for (j : k) {
                    read A[j][i];
                } 
            }
        }
    """, Diagnostic.Messages.ARRAY_INDEX_WRONG_ORDER, "A")
