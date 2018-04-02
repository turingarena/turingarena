from turingarena.tests.test_utils import assert_no_error, assert_error


def test_variable_not_initialized():
    assert_error("""
        main {
            var int a;
            write a;
        }
    """, "variable a used before initialization")


def test_variable_initialized():
    assert_no_error("""
        function f() -> int;
        main {
            var int a;
            call f() -> a;
            write a;
        }
    """)


def test_init_block_call():
    assert_no_error("""
        var int a;
        function f() -> int;
        init {
            call f() -> a;
        }
        main {
            write a;
        }
    """)


def test_call_on_itself():
    assert_error("""
        function f(int a) -> int;
        main {
            var int a;
            call f(a) -> a;
        }
    """, "variable a used before initialization")


def test_variable_not_initialized_subscript():
    assert_error("""
        main {
            var int a;
            var int[] A;
            read A[a];
        }
    """, "variable a used before initialization")


def test_variable_not_initialized_array():
    assert_no_error("""
        main {
            var int[] A;
            alloc A : 5;
            read A[0];
        }
    """)


def test_variable_not_allocated():
    assert_error("""
        main {
            var int[] a; 
            read a[0];
        }
    """, "variable a used before allocation")


def test_array_not_allocated():
    assert_error("""
        main {
            var int[] A;
            read A[0];
        }
    """, "variable A used before allocation")


def test_array_alloc():
    assert_no_error("""
        main {
            var int[] A; 
            alloc A : 10;
            read A[5];
            write A[5];
        }
    """)


def test_array_access():
    assert_no_error("""
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


def test_variable_initialized_for():
    assert_no_error("""
        main {
            var int a;
            read a;
            for (i : a) {
                write i;
            }
        }
    """)


def test_variable_initialized_if():
    assert_no_error("""
        main {
             var int a; 
             read a;
             if (a) {
                write 1;
             } else {
                write 2;
            }
        }
    """)


def test_variable_in_if_body():
    assert_error("""
        main {
            var int a;
            if (1) {
                write 1;
            } else {
                write a;
            }
        }
    """, "variable a used before initialization")


def test_variable_initialized_if_2():
    assert_no_error("""
        main {
             var int a;
             if (1) {
                 read a;
             } else {
                 read a;
             }
             write a;
        }
    """)


def test_variable_initialized_if_3():
    assert_error("""
        main {
             var int a, b;
             if (1) {
                 read b;
             } else {
                 read a;
             }
             write a;
        }
    """, "variable a used before initialization")


def test_variable_initialized_call():
    assert_no_error("""
        function test(int a, int b) -> int;
        
        main {
            var int a, b, c;
            read a, b;
            call test(a, b) -> c;
            write c; 
        }
    """)


def test_variable_not_initialized_call():
    assert_error("""
        function test(int a, int b) -> int;

        main {
            var int a, b, c;
            read a;
            call test(a, b) -> c;
            write c; 
        }
    """, "variable b used before initialization")


def test_local_variable():
    assert_no_error("""
        main {
            var int a;
            read a;
            write a;
        }
    """)


def test_local_variable_not_initialized():
    assert_error("""
         main {
            var int a;
            write a;
        }
    """, "variable a used before initialization")


def test_global_variables():
    assert_error("""
        var int a;
        
        init {
        }
        
        main {
        }
    """, "global variable a not initialized in init block")


def test_no_init_block():
    assert_error("""
        var int a;
        
        main {}
    """, "global variables declared but missing init block")


def test_init_block():
    assert_no_error("""
        var int a;
        
        init {
            read a;
        }
        
        main {
            write a;
        }
    """)


def test_variable_not_declared():
    assert_error("""
        main {
            write a;
        }
    """, "variable a not declared")


def test_variable_redeclared():
    assert_error("""
        var int a; 
        
        main {
            var int a;
        }
    """, "variable a redeclared")