import pytest

from turingarena.interface.interface import InterfaceDefinition
from turingarena.interface.expressions import VariableNotAllocatedError, VariableNotInitializedError


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


def test_variable_not_initialized_for():
    with pytest.raises(VariableNotInitializedError):
        InterfaceDefinition.compile("""
            var int a; 

            main {
                for (i : a) {
                    output i;
                }
            }
        """).static_analyze_variables()
