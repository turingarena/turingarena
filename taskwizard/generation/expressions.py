class ExpressionTypeExtractor:

    def __init__(self, scope):
        self.scope = scope

    def visit_variable_expression(self, e):
        return self.scope[e.variable_name].type

    def visit_subscript_expression(self, e):
        return extract_type(self.scope, e.array).item_type


def extract_type(scope, expression):
    return expression.accept(ExpressionTypeExtractor(scope))


class AbstractExpressionGenerator:

    def __init__(self, scope):
        self.scope = scope

    def generate(self, expression):
        return expression.accept(self)

    def visit_int_literal_expression(self, e):
        return str(e.value)

    def visit_variable_expression(self, e):
        return e.variable_name

    def visit_subscript_expression(self, e):
        return self.generate(e.array) + '[' + self.generate(e.index) + ']'
