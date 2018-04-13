from .test_utils import assert_interface_error, assert_no_interface_errors
from turingarena.interface.exceptions import Diagnostic


def test_variable_not_initialized_array():
    assert_no_interface_errors("""
        main {
            var int[] A;
            var int s; 
            read s;
            alloc A : s;
            for (i : s) {
                read A[i];
            }
        }
    """)


def test_array_not_allocated():
    assert_interface_error("""
        main {
            var int[] A;
            for (i : 10) {
                read A[i];
            }
        }
    """, Diagnostic.Messages.VARIABLE_NOT_ALLOCATED, "A")


def test_array_alloc():
    assert_interface_error("""
        main {
            var int[] A; 
            alloc A : 10;
            read A[5];
            write A[5];
        }
    """, Diagnostic.Messages.ARRAY_INDEX_NOT_VALID, "5")


def test_array_access():
    assert_no_interface_errors("""
        var int[] A;
        var int s;

        init {
            read s;
            alloc A : s;
            for (i : s) {
                read A[i];
            }
        }

        main {
            for (i : s) {
                write A[i];            
            }
        }
    """)


def test_array_basic():
    assert_no_interface_errors("""
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
                    read A[i][j];
                } 
            }
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
