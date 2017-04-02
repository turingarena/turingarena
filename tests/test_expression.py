import unittest

from taskwizard.definition.expr import IntLiteralExpression
from taskwizard.definition.semantics import Semantics
from taskwizard.parser import TaskParser

parser = TaskParser(semantics=Semantics())


class TestExpression(unittest.TestCase):

    def test_int_literal(self):
        expr = parser.parse("42", rule_name="expr")
        self.assertIsInstance(expr, IntLiteralExpression)
        self.assertEqual(expr.value, 42)
