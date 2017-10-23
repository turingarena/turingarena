from turingarena.protocol.codegen.expressions import AbstractReferenceExpressionBuilder, \
    AbstractValueExpressionBuilder
from turingarena.protocol.skeleton.cpp.types import build_type_expression
from turingarena.protocol.visitor import accept_expression


class ReferenceExpressionBuilder(AbstractReferenceExpressionBuilder):
    def visit_variable_expression(self, expr):
        return expr.variable_name + "_"

    def visit_subscript_expression(self, expr):
        return "{array}.item({index})".format(
            array=build_reference_expression(expr.array),
            index=build_value_expression(expr.index),
        )

    def visit_any_expression(self, expr):
        return "constant({type}, {expr})".format(
            type=build_type_expression(expr.type),
            expr=build_value_expression(expr),
        )

    def build_value(self, expr):
        return build_value_expression(expr)


class ValueExpressionBuilder(AbstractValueExpressionBuilder):

    def visit_any_expression(self, expr):
        return "get_value({expr})".format(expr=build_reference_expression(expr))


def build_value_expression(expr):
    return accept_expression(expr, visitor=ValueExpressionBuilder())


def build_reference_expression(expr):
    return accept_expression(expr, visitor=ReferenceExpressionBuilder())
