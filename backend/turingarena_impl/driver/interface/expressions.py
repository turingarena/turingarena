import logging
from abc import abstractmethod
from collections import namedtuple

from bidict import frozenbidict

from turingarena_impl.driver.generator import AbstractExpressionCodeGen
from turingarena_impl.driver.interface.common import AbstractSyntaxNodeWrapper
from turingarena_impl.driver.interface.context import ExpressionContext
from turingarena_impl.driver.interface.diagnostics import Diagnostic
from turingarena_impl.driver.interface.variables import Variable

logger = logging.getLogger(__name__)


class Expression:
    __slots__ = []

    @staticmethod
    def compile(ast, context: ExpressionContext):
        return expression_classes[ast.expression_type](ast, context)

    @property
    def expression_type(self):
        return self.ast.expression_type

    @abstractmethod
    def evaluate(self, bindings):
        pass

    @property
    def dimensions(self):
        return 0

    @abstractmethod
    def is_status(self, status):
        pass

    @property
    def reference(self):
        return None

    def is_reference_to(self, variable):
        return False

    def validate(self):
        return []

    def __str__(self):
        return AbstractExpressionCodeGen().expression(self)


class LiteralExpression(Expression, AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    @abstractmethod
    def value(self):
        pass

    def evaluate(self, bindings):
        return self.value

    def is_status(self, status):
        return True


class IntLiteralExpression(LiteralExpression):
    __slots__ = []

    @property
    def value(self):
        return int(self.ast.int_literal)


class VariableReferenceExpression(Expression, AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def expression_type(self):
        return "reference"

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

    def is_status(self, status):
        return self.reference in self.context.statement_context.get_references(status)

    def is_reference_to(self, variable):
        return self.variable == variable

    @property
    def reference(self):
        return self.variable.as_reference()

    def evaluate(self, bindings):
        return bindings[self.reference]

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
        return (
                self._get_referenced_variable() is not None
                or self.variable_name in self.context.statement_context.global_context.constants
        )


class SubscriptExpression(Expression, namedtuple("SubscriptExpression", [
    "array",
    "index",
    "context",
])):
    __slots__ = []

    @property
    def expression_type(self):
        return "subscript"

    @property
    def dimensions(self):
        return self.array.dimensions - 1

    def is_reference_to(self, variable):
        return False

    def is_status(self, status):
        return (
                self.reference in self.context.statement_context.get_references(status)
                or self.array.is_status(status)
        )

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

    def evaluate(self, bindings):
        if self.reference in bindings:
            return bindings[self.reference]
        else:
            return self.array.evaluate(bindings)[
                self.index.evaluate(bindings)
            ]


class SyntheticExpression:
    __slots__ = ["expression_type", "__dict__"]

    def __init__(self, expression_type, **kwargs):
        self.expression_type = expression_type
        self.__dict__ = kwargs


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
        return SubscriptExpression(array, index, context)
    else:
        return VariableReferenceExpression(ast, context)


def compile_reference_expression(ast, context):
    return compile_subscript(ast, ast.indices, context)


expression_classes = frozenbidict({
    "int_literal": IntLiteralExpression,
    "reference_subscript": compile_reference_expression,
    "nested": lambda ast, context: Expression.compile(ast.expression, context),
})
