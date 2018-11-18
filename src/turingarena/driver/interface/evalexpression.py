from turingarena.driver.interface.expressions import ExpressionVisitor


class ExpressionEvaluator(ExpressionVisitor):
    def __init__(self, bindings):
        self.bindings = bindings

    def visit_IntLiteralExpression(self, e):
        return e.value

    def visit_VariableReferenceExpression(self, e):
        return self.bindings[e.reference]

    def visit_SubscriptExpression(self, e):
        if e.reference in self.bindings:
            return self.bindings[e.reference]
        else:
            return self.visit(e.array)[self.visit(e.index)]


def evaluate_expression(e, bindings):
    return ExpressionEvaluator(bindings).visit(e)
