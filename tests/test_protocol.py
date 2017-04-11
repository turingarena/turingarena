import unittest

from taskwizard.definition.protocol import InputStep, OutputStep, CallStep, ForNode, SwitchNode, SwitchCase, \
    ProtocolNode


class TestProtocol(unittest.TestCase):

    def test_input(self):
        step = ProtocolNode.Definition.parse("input N, M;")
        self.assertIsInstance(step, InputStep.Definition)
        self.assertEqual(len(step.variables), 2)

    def test_output(self):
        step = ProtocolNode.Definition.parse("output N, M;")
        self.assertIsInstance(step, OutputStep.Definition)
        self.assertEqual(len(step.variables), 2)

    def test_call_returns(self):
        step = ProtocolNode.Definition.parse("call A = f(B, C);")
        self.assertIsInstance(step, CallStep.Definition)
        self.assertEqual(step.function_name, "f")

    def test_call_no_return(self):
        step = ProtocolNode.Definition.parse("call f(B, C);")
        self.assertIsInstance(step, CallStep.Definition)
        self.assertEqual(step.function_name, "f")
        self.assertFalse(hasattr(step, "return_value"))

    def test_for(self):
        step = ProtocolNode.Definition.parse("for (i : 1..10) {}")
        self.assertIsInstance(step, ForNode.Definition)
        self.assertEqual(step.index, "i")

    def test_switch(self):
        step = ProtocolNode.Definition.parse("switch (X[i]) { case(A) {} case(B) {} }")
        self.assertIsInstance(step, SwitchNode.Definition)
        cases = step.cases
        self.assertEqual(len(cases), 2)
        self.assertIsInstance(cases[0], SwitchCase.Definition)
        self.assertEqual(cases[0].value, "A")
