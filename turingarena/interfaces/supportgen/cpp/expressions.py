from turingarena.interfaces.codegen.expressions import DefaultLeftValueBuilder, DefaultRightValueBuilder
from turingarena.interfaces.visitor import accept_expression


class RightValueBuilder(DefaultRightValueBuilder):

    def on_left_value(self, expr):
        return generate_lvalue(expr)


def generate_lvalue(expression):
    return accept_expression(expression, visitor=DefaultLeftValueBuilder(generate_expression))


def generate_expression(expression):
    return accept_expression(expression, visitor=RightValueBuilder(generate_lvalue))
