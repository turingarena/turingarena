import pytest

from turingarena.interface.interface import InterfaceDefinition
from turingarena.interface.exceptions import *


def assert_no_error(text):
    i = InterfaceDefinition.compile(text)
    for m in i.validate():
        print(m.message)
        raise AssertionError


def assert_error(text, error):
    i = InterfaceDefinition.compile(text)
    for m in i.validate():
        if m.message == error:
            return
    raise AssertionError


def test_variable_not_initialized():
    assert_error("""
        main {
            var int a;
            output a;
        }
    """, "variable a used before initialization")


def test_variable_initialized():
    assert_no_error("""
        function f() -> int;
        main {
            var int a;
            call f() -> a;
            output a;
        }
    """)


def test_init_block():
    assert_no_error("""
        var int a;
        function f() -> int;
        init {
            f() -> a;
        }
        main {
            output a;
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
            input A[a];
        }
    """, "variable a used before initialization")


def test_variable_not_initialized_array():
    assert_no_error("""
        main {
            var int[] A;
            alloc A : 5;
            input A[0];
        }
    """)


def test_variable_not_allocated():
    assert_error("""
        main {
            var int[] a; 
            input a[0];
        }
    """, "variable a used before allocation")


def test_array_not_allocated():
    assert_error("""
        main {
            var int[] A;
            input A[0];
        }
    """, "variable A used before allocation")


def test_array_alloc():
    assert_no_error("""
        main {
            var int[] A; 
            alloc A : 10;
            input A[5];
            output A[5];
        }
    """)


def test_array_access():
    assert_no_error("""
        var int[] A;
        var int s;
        
        init {
            input s;
            alloc A : s;
            for (i : s) {
                input A[i];
            }
        }
        
        main {
            for (i : s) {
                output A[i];            
            }
        }
    """)


def test_variable_initialized_for():
    assert_no_error("""
        main {
            var int a;
            input a;
            for (i : a) {
                output i;
            }
        }
    """)


def test_variable_initialized_if():
    assert_no_error("""
        main {
             var int a; 
             input a;
             if (a) {
                output 1;
             } else {
                output 2;
            }
        }
    """)


def test_variable_in_if_body():
    assert_error("""
        main {
            var int a;
            if (1) {
                output 1;
            } else {
                output a;
            }
        }
    """, "variable a used before initialization")


def test_variable_initialized_call():
    assert_no_error("""
        function test(int a, int b) -> int;
        
        main {
            var int a, b, c;
            input a, b;
            call test(a, b) -> c;
            output c; 
        }
    """)


def test_variable_not_initialized_call():
    assert_error("""
        function test(int a, int b) -> int;

        main {
            var int a, b, c;
            input a;
            call test(a, b) -> c;
            output c; 
        }
    """, "variable b used before initialization")


def test_local_variable():
    assert_no_error("""
        main {
            var int a;
            input a;
            output a;
        }
    """)


def test_local_variable_not_initialized():
    assert_error("""
         main {
            var int a;
            output a;
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
            input a;
        }
        
        main {
            output a;
        }
    """)


def test_variable_not_defined():
    assert_error("""
        main {
            output a;
        }
    """, "variable a not declared")


def test_function_not_defined():
    assert_error("""
        main {
            call f();
        }
    """, "function f not declared")


def test_wrong_parameters():
    assert_error("""
        function f(int a);
        main {
            call f();
        }
    """, "function f expects 1 argument(s), got 0")


def test_function_wrong_type():
    assert_error("""
        function f(int[] a);
        main {
            call f(5);
        }
    """, "argument a of function f: expected int[], got int")


def test_function_return_value():
    assert_error("""
        function f() -> int;
        main {
            call f();
        }
    """, "function f returns int, but no return expression given")


def test_function_no_return_value():
    assert_error("""
        function f();
        main {
            var int a;
            call f() -> a;
        }
    """, "function f does not return a value")