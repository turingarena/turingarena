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
        assert m.message == error


def test_variable_not_initialized():
    assert_error("""
            main {
                var int a;
                output a;
            }
    """, "variable a used before initialization")


def test_variable_not_allocated():
    assert_error("""
            main {
                var int[] a; 
                input a[0];
            }
    """, "variable a used before allocation")


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


def test_function_not_defined_error():
    assert_error("""              
            main {
                call a();
            }
        """, "")

def test_wrong_function_call():
    with pytest.raises(FunctionCallError):
        InterfaceDefinition.compile("""   
            function a(int a);

            main {
                call a();
            }
        """).static_analysis()

