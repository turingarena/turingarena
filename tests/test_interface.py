import unittest

from taskwizard.definition.interface import InterfaceDefinition
from taskwizard.definition.protocol import InputStep, OutputStep, CallStep, ForNode, SwitchNode, SwitchCase, \
    ProtocolNode


class TestInterface(unittest.TestCase):

    def test_empty(self):
        interface = InterfaceDefinition.parse("""
            interface exampleinterface {}
        """)

        self.assertEqual([], interface.get_function_definitions())
        self.assertEqual([], interface.get_variable_definitions())
        self.assertEqual([], interface.get_callback_function_definitions())
        self.assertEqual([], interface.get_protocol_definitions())

    def test_full(self):
        interface = InterfaceDefinition.parse("""
            interface exampleinterface {
                int A;
                int fun(int B);
                callback int callbackfun(int C);
                protocol {}
            }
        """)

        self.assertEqual(1, len(interface.get_function_definitions()))
        self.assertEqual(1, len(interface.get_variable_definitions()))
        self.assertEqual(1, len(interface.get_callback_function_definitions()))
        self.assertEqual(1, len(interface.get_protocol_definitions()))
