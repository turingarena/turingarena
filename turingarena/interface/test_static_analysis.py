import pytest

from turingarena.interface.interface import InterfaceDefinition
from turingarena.interface.expressions import VariableNotAllocatedError, VariableNotInitializedError, VariableNotDeclaredError


def test_variable_not_initialized():
    with pytest.raises(VariableNotInitializedError):
        InterfaceDefinition.compile("""
            var int a; 
            
            main {
                output a;
            }
        """).static_analyze_variables()


def test_variable_not_allocated():
    with pytest.raises(VariableNotAllocatedError):
        InterfaceDefinition.compile("""
            var int[] a; 

            main {
                input a[0];
            }
        """).static_analyze_variables()


def test_variable_initialized_for():
    InterfaceDefinition.compile("""
            var int a; 

            main {
                input a;
                for (i : a) {
                    output i;
                }
            }
    """).static_analyze_variables()


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
    """).static_analyze_variables()


def test_local_variable():
    InterfaceDefinition.compile("""
            main {
                var int a;
                input a;
                output a;
            }
    """).static_analyze_variables()


def test_local_variable_not_initialized():
    with pytest.raises(VariableNotInitializedError):
        InterfaceDefinition.compile("""
            main {
                var int a;
                output a;
            }
        """).static_analyze_variables()


def test_variable_not_defined():
    with pytest.raises(VariableNotDeclaredError):
        InterfaceDefinition.compile("""
        main {
            output a;
        }
        """).static_analyze_variables()
