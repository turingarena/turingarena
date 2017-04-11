import unittest

from taskwizard.definition.expression import IntLiteralExpression, Expression, VariableExpression


class TestExpression(unittest.TestCase):

    def test_int_literal(self):
        expr = Expression.parse("42")
        self.assertIsInstance(expr, IntLiteralExpression)
        self.assertEqual(expr.value, 42)

    def test_variable(self):
        expr = Expression.parse("V[1][A[2]]")
        self.assertIsInstance(expr, VariableExpression)
        self.assertEqual(expr.variable_name, "V")
        index1, index2 = expr.indexes
        self.assertEqual(index1.value, 1)
        self.assertEqual(index2.variable_name, "A")
