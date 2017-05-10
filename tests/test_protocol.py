import unittest

from taskwizard.definition.protocol import *


class TestProtocol(unittest.TestCase):

    def test_input(self):
        statement = ProtocolStatementDefinition.parse("input N, M;")
        self.assertIsInstance(statement, InputStatementDefinition)
        self.assertEqual(len(statement.variables), 2)

    def test_output(self):
        statement = ProtocolStatementDefinition.parse("output N, M;")
        self.assertIsInstance(statement, OutputStatementDefinition)
        self.assertEqual(len(statement.variables), 2)

    def test_call_returns(self):
        statement = ProtocolStatementDefinition.parse("call A = f(B, C);")
        self.assertIsInstance(statement, CallStatementDefinition)
        self.assertEqual(statement.function_name, "f")

    def test_call_no_return(self):
        statement = ProtocolStatementDefinition.parse("call f(B, C);")
        self.assertIsInstance(statement, CallStatementDefinition)
        self.assertEqual(statement.function_name, "f")
        self.assertIsNone(statement.return_value)

    def test_for(self):
        statement = ProtocolStatementDefinition.parse("for (i : 1..10) {}")
        self.assertIsInstance(statement, ForStatementDefinition)
        self.assertEqual(statement.index.name, "i")

    def test_switch(self):
        statement = ProtocolStatementDefinition.parse("switch (X[i]) { case(A) {} case(B) {} }")
        self.assertIsInstance(statement, SwitchStatementDefinition)
        cases = statement.cases
        self.assertEqual(len(cases), 2)
        self.assertIsInstance(cases[0], SwitchCaseDefinition)
        self.assertEqual(cases[0].value, "A")
