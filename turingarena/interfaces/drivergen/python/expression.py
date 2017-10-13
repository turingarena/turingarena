from turingarena.interfaces.codegen.expressions import DefaultLeftValueBuilder, DefaultRightValueBuilder
from turingarena.interfaces.supportgen.cpp.types import build_type_expression
from turingarena.interfaces.visitor import accept_expression


class LeftValueBuilder(DefaultLeftValueBuilder):
    def visit_variable_expression(self, expr):
        return expr.variable_name + "_"

    def visit_subscript_expression(self, expr):
        return "{array}.item({index})".format(
            array=build_left_value_expression(expr.array),
            index=build_right_value_expression(expr.index),
        )

    def on_right_value(self, expr):
        return "constant({type}, {expr})".format(
            type=build_type_expression(expr.type),
            expr=build_right_value_expression(expr),
        )


class RightValueBuilder(DefaultRightValueBuilder):

    def on_left_value(self, expr):
        return "get_value({expr})".format(expr=build_left_value_expression(expr))


def build_right_value_expression(expr):
    return accept_expression(expr, visitor=RightValueBuilder(build_left_value_expression))


def build_left_value_expression(expr):
    return accept_expression(expr, visitor=LeftValueBuilder(build_right_value_expression))
