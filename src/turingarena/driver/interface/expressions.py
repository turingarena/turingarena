import logging
from abc import abstractmethod
from collections import namedtuple

from bidict import frozenbidict

from turingarena.driver.interface.common import AbstractSyntaxNodeWrapper
from turingarena.driver.interface.context import ExpressionContext
from turingarena.driver.interface.diagnostics import Diagnostic
from turingarena.driver.interface.variables import Variable
from turingarena.util.visitor import Visitor

logger = logging.getLogger(__name__)


class Expression:
    __slots__ = []

    @staticmethod
    def compile(ast, context: ExpressionContext):
        return expression_classes[ast.expression_type](ast, context)

    @property
    def reference(self):
        return None

    def is_reference_to(self, variable):
        return False

    def validate(self):
        return []


class Literal(Expression):
    __slots__ = []

    @property
    @abstractmethod
    def value(self):
        pass


class IntLiteral(Literal):
    __slots__ = []


class IntLiteralAst(IntLiteral, AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def value(self):
        return int(self.ast.int_literal)


class IntLiteralSynthetic(
    namedtuple("IntLiteralSynthetic", ["value"]),
    IntLiteral,
):
    __slots__ = []


class VariableReference(Expression, AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def variable_name(self):
        return self.ast.variable_name

    @property
    def dimensions(self):
        return self.variable.dimensions

    @property
    def variable(self):
        declared = Variable(
            name=self.variable_name,
            dimensions=self.context.index_count,
        )
        if self.context.declaring:
            return declared
        else:
            referenced = self._get_referenced_variable()
            if referenced is None:  # quirk
                return declared
            return referenced

    def _get_referenced_variable(self):
        variable_mapping = self.context.statement_context.variable_mapping
        return variable_mapping.get(self.variable_name, None)

    def is_reference_to(self, variable):
        return self.variable == variable

    @property
    def reference(self):
        return self.variable.as_reference()

    def validate(self):
        if not self.context.declaring and not self._is_declared():
            yield Diagnostic(
                Diagnostic.Messages.VARIABLE_NOT_DECLARED,
                self.variable_name,
                parseinfo=self.ast.parseinfo,
            )
        if self.context.declaring and self._is_declared():
            yield Diagnostic(
                Diagnostic.Messages.VARIABLE_REUSED,
                self.variable_name,
                parseinfo=self.ast.parseinfo,
            )

    def _is_declared(self):
        return self._get_referenced_variable() is not None


class Subscript(Expression, namedtuple("Subscript", [
    "array",
    "index",
    "context",
])):
    __slots__ = []

    @property
    def dimensions(self):
        return self.array.dimensions - 1

    def is_reference_to(self, variable):
        return False

    @property
    def expected_for_index(self):
        reversed_indexes = self.context.statement_context.index_variables[::-1]
        try:
            return reversed_indexes[self.context.index_count]
        except IndexError:
            return None

    def validate(self):
        yield from self.array.validate()
        yield from self.index.validate()

        if self.context.reference:
            yield from self._validate_reference_index()

    def _validate_reference_index(self):
        if self.expected_for_index is None:
            yield Diagnostic(
                Diagnostic.Messages.UNEXPECTED_ARRAY_INDEX,
                parseinfo=self.index.ast.parseinfo,
            )
            return
        if not self._is_reference_index():
            yield Diagnostic(
                Diagnostic.Messages.WRONG_ARRAY_INDEX,
                self.expected_for_index.variable.name,
                parseinfo=self.index.ast.parseinfo,
            )

    def _is_reference_index(self):
        expected_index = self.expected_for_index
        if expected_index is None:
            return None
        return self.index.is_reference_to(expected_index.variable)

    @property
    def reference(self):
        array = self.array.reference
        if array is None:
            return None
        if not self.context.declaring and not self._is_reference_index():
            return None
        return array._replace(
            index_count=array.index_count + 1,
        )


def compile_subscript(ast, index_asts, context):
    if index_asts:
        array = compile_subscript(ast, index_asts[:-1], context._replace(
            index_count=context.index_count + 1,
        ))
        index = Expression.compile(index_asts[-1], context._replace(
            declaring=False,
            resolved=True,
            reference=False,
            index_count=0,
        ))
        return Subscript(array, index, context)
    else:
        return VariableReference(ast, context)


def compile_reference_expression(ast, context):
    return compile_subscript(ast, ast.indices, context)


expression_classes = frozenbidict({
    "int_literal": IntLiteralAst,
    "reference_subscript": compile_reference_expression,
    "nested": lambda ast, context: Expression.compile(ast.expression, context),
})


class ExpressionVisitor(Visitor):
    def visit_Expression(self, e):
        raise NotImplementedError

    def visit_Literal(self, e):
        return NotImplemented

    def visit_IntLiteral(self, e):
        return NotImplemented

    def visit_VariableReference(self, e):
        return NotImplemented

    def visit_Subscript(self, e):
        return NotImplemented
