import unittest

from taskwizard.parser import TaskParser
from taskwizard.protocol import InputStep, OutputStep, CallStep, ForNode, SwitchNode, SwitchCase
from taskwizard.semantics import Semantics

parser = TaskParser(semantics=Semantics())


class TestProtocol(unittest.TestCase):

    def test_input(self):
        step = parser.parse("input N, M;", rule_name="protocol_node")
        self.assertIsInstance(step, InputStep)
        self.assertEqual(len(step.items), 2)

    def test_output(self):
        step = parser.parse("output N, M;", rule_name="protocol_node")
        self.assertIsInstance(step, OutputStep)
        self.assertEqual(len(step.items), 2)

    def test_call_returns(self):
        step = parser.parse("call A = f(B, C);", rule_name="protocol_node")
        self.assertIsInstance(step, CallStep)
        self.assertEqual(step.function_name, "f")

    def test_call_no_return(self):
        step = parser.parse("call f(B, C);", rule_name="protocol_node")
        self.assertIsInstance(step, CallStep)
        self.assertEqual(step.function_name, "f")
        self.assertIsNone(step.return_value)

    def test_for(self):
        step = parser.parse("for (i : 1..10) {}", rule_name="protocol_node")
        self.assertIsInstance(step, ForNode)
        self.assertEqual(step.index, "i")

    def test_switch(self):
        step = parser.parse("switch (X[i]) { case(A) {} case(B) {} }", rule_name="protocol_node")
        self.assertIsInstance(step, SwitchNode)
        cases = step.cases
        self.assertEqual(len(cases), 2)
        self.assertIsInstance(cases[0], SwitchCase)
        self.assertEqual(cases[0].value, "A")
