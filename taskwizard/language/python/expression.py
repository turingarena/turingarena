from taskwizard.generation.expressions import AbstractExpressionGenerator
from taskwizard.generation.scope import Scope
from taskwizard.generation.utils import indent_all, indent
from taskwizard.grammar import SyntaxVisitor


class DriverVariableExpressionBuilder(SyntaxVisitor):

    def __init__(self, expr):
        self.expr = expr

    def visit_global_declaration(self, declaration):
        return "self.{name}".format(
            name=self.expr.variable_name,
        )

    def visit_local_declaration(self, declaration):
        return self.expr.variable_name

    def visit_parameter_declaration(self, declaration):
        return self.expr.variable_name

    def visit_index_declaration(self, declaration):
        return self.expr.variable_name


class DriverExpressionGenerator(AbstractExpressionGenerator):

    def visit_variable_expression(self, e):
        declaration = self.scope[e.variable_name]
        return DriverVariableExpressionBuilder(e).visit(declaration)


def build_driver_expression(scope, expr):
    return DriverExpressionGenerator(scope).visit(expr)