import unittest

from taskwizard.definition.interface import InterfaceDefinition


class TestInterface(unittest.TestCase):

    def test_empty(self):
        interface = InterfaceDefinition.parse("""
            interface exampleinterface {}
        """)

        self.assertEqual([], interface.function_definitions)
        self.assertEqual([], interface.variable_definitions)
        self.assertEqual([], interface.callback_function_definitions)
        self.assertEqual([], interface.protocol_definitions)

    def test_full(self):
        interface = InterfaceDefinition.parse("""
            interface exampleinterface {
                int A;
                int fun(int B);
                callback int callbackfun(int C);
                protocol {}
            }
        """)

        self.assertEqual(1, len(interface.function_definitions))
        self.assertEqual(1, len(interface.variable_definitions))
        self.assertEqual(1, len(interface.callback_function_definitions))
        self.assertEqual(1, len(interface.protocol_definitions))
