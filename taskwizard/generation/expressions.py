class ExpressionVisitor:

    def visit(self, expression):
        method = getattr(self, "visit_%s" % expression.parseinfo.rule)
        return method(expression)


class VariableExpressionVisitor(ExpressionVisitor):

    def __init__(self, scope):
        self.scope = scope

    def visit_variable_expression(self, expression):
        return self.scope[expression.variable_name]


class AbstractExpressionGenerator(ExpressionVisitor):

    def generate(self, expression):
        return self.visit(expression)

    def visit_int_literal_expression(self, e):
        return str(e.value)

    def visit_variable_expression(self, e):
        return e.variable_name + ''.join(
            '[' + self.generate(i) + ']'
            for i in e.indexes
        )