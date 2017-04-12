import unittest

from taskwizard.definition.protocol import *


class TestProtocol(unittest.TestCase):

    def test_input(self):
        step = ProtocolNodeDefinition.parse("input N, M;")
        self.assertIsInstance(step, InputStepDefinition)
        self.assertEqual(len(step.variables), 2)

    def test_output(self):
        step = ProtocolNodeDefinition.parse("output N, M;")
        self.assertIsInstance(step, OutputStepDefinition)
        self.assertEqual(len(step.variables), 2)

    def test_call_returns(self):
        step = ProtocolNodeDefinition.parse("call A = f(B, C);")
        self.assertIsInstance(step, CallStepDefinition)
        self.assertEqual(step.function_name, "f")

    def test_call_no_return(self):
        step = ProtocolNodeDefinition.parse("call f(B, C);")
        self.assertIsInstance(step, CallStepDefinition)
        self.assertEqual(step.function_name, "f")
        self.assertIsNone(step.return_value)

    def test_for(self):
        step = ProtocolNodeDefinition.parse("for (i : 1..10) {}")
        self.assertIsInstance(step, ForNodeDefinition)
        self.assertEqual(step.index.name, "i")

    def test_switch(self):
        step = ProtocolNodeDefinition.parse("switch (X[i]) { case(A) {} case(B) {} }")
        self.assertIsInstance(step, SwitchNodeDefinition)
        cases = step.cases
        self.assertEqual(len(cases), 2)
        self.assertIsInstance(cases[0], SwitchCaseDefinition)
        self.assertEqual(cases[0].value, "A")
