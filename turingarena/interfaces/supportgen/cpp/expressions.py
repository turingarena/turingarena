from turingarena.interfaces.codegen.expressions import AbstractValueExpressionBuilder, \
    AbstractReferenceExpressionBuilder
from turingarena.interfaces.visitor import accept_expression


class ReferenceExpressionBuilder(AbstractReferenceExpressionBuilder):

    def build_value(self, expr):
        return generate_expression(expr)


class ValueExpressionBuilder(AbstractValueExpressionBuilder):

    def build_reference(self, expr):
        return generate_reference_expression(expr)

    def visit_any_expression(self, expr):
        return self.build_reference(expr)


def generate_reference_expression(expression):
    return accept_expression(expression, visitor=ReferenceExpressionBuilder())


def generate_expression(expression):
    return accept_expression(expression, visitor=ValueExpressionBuilder())
