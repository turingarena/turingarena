import unittest

from taskwizard.expr import IntLiteralExpression
from taskwizard.parser import TaskParser
from taskwizard.semantics import Semantics

parser = TaskParser(semantics=Semantics())


class TestExpression(unittest.TestCase):

    def test_int_literal(self):
        expr = parser.parse("42", rule_name="expr")
        self.assertIsInstance(expr, IntLiteralExpression)
        self.assertEqual(expr.value, 42)
