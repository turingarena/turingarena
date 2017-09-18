from turingarena.interfaces.codegen.expressions import AbstractExpressionGenerator
from turingarena.interfaces.drivergen.python.types import TypeBuilder


class DriverExpressionBuilder(AbstractExpressionGenerator):
    def build(self, expr):
        return expr.accept(self)

    def visit_variable_expression(self, expr):
        return expr.variable_name + "_[:]"


class AssignableExpressionBuilder:
    def visit_int_literal_expression(self, expr):
        return self.wrap_in_scalar(expr)

    def wrap_in_scalar(self, expr):
        return "constant({type}, {expr})[:]".format(
            type=TypeBuilder().build(expr.type),
            expr=self.visit_default(expr),
        )

    def build(self, expr):
        return expr.accept(self)

    def visit_default(self, e):
        return DriverExpressionBuilder().build(e)


def build_driver_expression(expr):
    return DriverExpressionBuilder().build(expr)


def build_assignable_expression(expr):
    return AssignableExpressionBuilder().build(expr)
