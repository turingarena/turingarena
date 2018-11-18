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


class ExpressionStatusAnalyzer(ExpressionVisitor):
    def __init__(self, context, status):
        self.context = context
        self.status = status

    def visit_LiteralExpression(self, e):
        return True

    def visit_VariableReferenceExpression(self, e):
        return e.reference in self.context.get_references(self.status)

    def visit_SubscriptExpression(self, e):
        return (
                e.reference in self.context.get_references(self.status)
                or self.visit(e.array)
        )


class ExpressionDimensionAnalyzer(ExpressionVisitor):
    def visit_LiteralExpression(self, e):
        return 0

    def visit_VariableReferenceExpression(self, e):
        return e.variable.dimensions

    def visit_SubscriptExpression(self, e):
        return self.visit(e.array) - 1
