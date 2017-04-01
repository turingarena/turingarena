import unittest

from taskwizard.parser import TaskParser
from taskwizard.protocol import InputStep, OutputStep, CallStep
from taskwizard.semantics import Semantics

parser = TaskParser(semantics=Semantics())


class TestProtocol(unittest.TestCase):

    def test_input(self):
        step = parser.parse("input N, M;", rule_name="protocol_step")
        self.assertIsInstance(step, InputStep)
        self.assertEqual(len(step.items), 2)

    def test_output(self):
        step = parser.parse("output N, M;", rule_name="protocol_step")
        self.assertIsInstance(step, OutputStep)
        self.assertEqual(len(step.items), 2)

    def test_call_returns(self):
        step = parser.parse("call A = f(B, C);", rule_name="protocol_step")
        self.assertIsInstance(step, CallStep)
        self.assertEqual(step.function_name, "f")

    def test_call_no_return(self):
        step = parser.parse("call f(B, C);", rule_name="protocol_step")
        self.assertIsInstance(step, CallStep)
        self.assertEqual(step.function_name, "f")
