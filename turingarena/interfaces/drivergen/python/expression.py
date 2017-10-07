from turingarena.interfaces.visitor import accept_expression

from turingarena.interfaces.codegen.expressions import AbstractExpressionGenerator
from turingarena.interfaces.drivergen.python.types import TypeBuilder


class DriverExpressionBuilder(AbstractExpressionGenerator):
    def visit_variable_expression(self, expr):
        return expr.variable_name + "_[:]"


class AssignableExpressionBuilder:
    def visit_int_literal_expression(self, expr):
        return self.wrap_in_scalar(expr)

    def wrap_in_scalar(self, expr):
        return "constant({type}, {expr})[:]".format(
            type=TypeBuilder().build(expr.type),
            expr=self.visit_any_expression(expr),
        )

    def visit_any_expression(self, e):
        return build_driver_expression(e)


def build_driver_expression(expr):
    return accept_expression(expr, visitor=DriverExpressionBuilder())


def build_assignable_expression(expr):
    return accept_expression(expr, visitor=AssignableExpressionBuilder())
