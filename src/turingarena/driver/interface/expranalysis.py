from collections import namedtuple

from turingarena.driver.interface.diagnostics import Diagnostic
from turingarena.driver.interface.expressions import ExpressionVisitor
from turingarena.driver.interface.variables import Reference, Variable


class ExpressionStatusAnalyzer(ExpressionVisitor):
    def __init__(self, context, status):
        self.context = context
        self.status = status

    def visit_Literal(self, e):
        return True

    def visit_VariableReference(self, e):
        return e.reference in self.context.get_references(self.status)

    def visit_Subscript(self, e):
        return (
                e.reference in self.context.get_references(self.status)
                or self.visit(e.array)
        )


class ExpressionDimensionAnalyzer(ExpressionVisitor):
    def visit_Literal(self, e):
        return 0

    def visit_VariableReference(self, e):
        return e.variable.dimensions

    def visit_Subscript(self, e):
        return self.visit(e.array) - 1


class ExpressionReferenceExtractor(
    ExpressionVisitor,
    namedtuple("ExpressionReferenceExtractor", ["dimensions"])
):
    def visit_VariableReference(self, e):
        return Reference(
            variable=Variable(name=e.variable_name, dimensions=self.dimensions),
            index_count=0,
        )

    def visit_Subscript(self, e):
        array = self.visit(e.array)
        if array is None:
            return None
        return array._replace(
            index_count=array.index_count + 1,
        )

    def visit_Expression(self, e):
        return None


class ReferenceExpressionValidator(
    ExpressionVisitor,
    namedtuple("ReferenceExpressionValidator", ["context", "dimensions"])
):
    """
    Checks that the given expression is a valid reference with `self.dimensions` dimension.
    """

    def visit_Expression(self, e):
        # TODO: new diagnostic classes
        yield "invalid declaration expression"

    def visit_VariableReference(self, e):
        if e.variable in self.context.variable_mapping:
            yield Diagnostic(
                Diagnostic.Messages.VARIABLE_REUSED,
                e.variable.name,
                parseinfo=e.ast.parseinfo,
            )
        if e.variable.dimensions != self.dimensions:
            yield "wrong number of subscripts"

    def visit_Subscript(self, e):
        if self.dimensions >= len(self.context.index_variables):
            yield Diagnostic(
                Diagnostic.Messages.UNEXPECTED_ARRAY_INDEX,
                parseinfo=e.index.ast.parseinfo,
            )
            return

        expected_index = self.context.index_variables[::-1][self.dimensions]
        if not ExpressionDirectReferenceAnalyzer(expected_index).visit(e):
            yield Diagnostic(
                Diagnostic.Messages.WRONG_ARRAY_INDEX,
                expected_index.variable.name,
                parseinfo=e.index.ast.parseinfo,
            )

        yield from self._replace(dimensions=self.dimensions + 1).visit(e.array)


class ExpressionDirectReferenceAnalyzer(ExpressionVisitor):
    def __init__(self, target_variable):
        self.target_variable = target_variable

    def visit_VariableReference(self, e):
        return e.variable == self.target_variable

    def visit_Expression(self, e):
        return False
