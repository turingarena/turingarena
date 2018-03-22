import pytest

from turingarena.interface.interface import InterfaceDefinition
from turingarena.interface.exceptions import *


def test_variable_not_initialized():
    with pytest.raises(VariableNotInitializedError):
        InterfaceDefinition.compile("""
            var int a; 
            
            main {
                output a;
            }
        """).static_analysis()


def test_variable_not_allocated():
    with pytest.raises(VariableNotAllocatedError):
        InterfaceDefinition.compile("""
            var int[] a; 

            main {
                input a[0];
            }
        """).static_analysis()


def test_variable_initialized_for():
    InterfaceDefinition.compile("""
            var int a; 

            main {
                input a;
                for (i : a) {
                    output i;
                }
            }
    """).static_analysis()


def test_variable_initialized_if():
    InterfaceDefinition.compile("""
            var int a; 

            main {
                input a;
                if (a) {
                    output 1;
                } else {
                    output 2;
                }
            }
    """).static_analysis()


def test_variable_initialized_call():
    InterfaceDefinition.compile("""
        function test(int a, int b) -> int;
        
        main {
            var int a, b, c;
            input a, b;
            call test(a, b) -> c;
            output c; 
        }
    """)


def test_variable_not_initialized_call():
    InterfaceDefinition.compile("""
        function test(int a, int b) -> int;

        main {
            var int a, b, c;
            input a;
            call test(a, b) -> c;
            output c; 
        }
    """)


def test_local_variable():
    InterfaceDefinition.compile("""
            main {
                var int a;
                input a;
                output a;
            }
    """).static_analysis()


def test_local_variable_not_initialized():
    with pytest.raises(VariableNotInitializedError):
        InterfaceDefinition.compile("""
            main {
                var int a;
                output a;
            }
        """).static_analysis()


def test_variable_not_defined():
    with pytest.raises(VariableNotDeclaredError):
        InterfaceDefinition.compile("""
        main {
            output a;
        }
        """).static_analysis()


def test_global_variables():
    with pytest.raises(GlobalVariableNotInitializedError):
        InterfaceDefinition.compile("""
        var int a, b;
        
        init {
            input a;
        }
        
        main {
            input b;
        }
        """).static_analysis()


def test_function_not_defined_error():
    with pytest.raises(FunctionNotDeclaredError):
        InterfaceDefinition.compile("""              
            main {
                call a();
            }
        """).static_analysis()


def test_wrong_function_call():
    with pytest.raises(FunctionCallError):
        InterfaceDefinition.compile("""   
            function a(int a);

            main {
                call a();
            }
        """).static_analysis()

