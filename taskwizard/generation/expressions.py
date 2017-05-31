class ExpressionVisitor:

    def visit(self, expression):
        method = getattr(self, "visit_%s" % expression.parseinfo.rule)
        return method(expression)


class VariableExpressionVisitor(ExpressionVisitor):

    def __init__(self, scope):
        self.scope = scope

    def visit_variable_expression(self, expression):
        return self.scope[expression.variable_name]
