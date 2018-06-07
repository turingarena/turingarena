import logging
from abc import abstractmethod
from itertools import zip_longest

from bidict import frozenbidict

from turingarena_impl.interface.common import AbstractSyntaxNodeWrapper
from turingarena_impl.interface.diagnostics import Diagnostic
from turingarena_impl.interface.variables import Reference, Variable

logger = logging.getLogger(__name__)


class Expression(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @staticmethod
    def compile(ast, context):
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

    @property
    def reference(self):
        return None

    def is_reference_to(self, variable):
        return False

    def validate(self):
        return []

    def validate_reference(self):
        return []

    def validate_resolved(self):
        return []


class LiteralExpression(Expression):
    __slots__ = []

    @property
    @abstractmethod
    def value(self):
        pass

    def evaluate(self, bindings):
        return self.value


class IntLiteralExpression(LiteralExpression):
    __slots__ = []

    @property
    def value(self):
        return int(self.ast.int_literal)


class ReferenceExpression(Expression):
    __slots__ = []

    @property
    def variable_name(self):
        return self.ast.variable_name

    @property
    def variable(self):
        # FIXME: using 'get' for both declarations and as quirk, should we?
        return self.context.variable_mapping.get(
            self.variable_name,
            Variable(
                name=self.variable_name,
                dimensions=len(self.indices),
            ),
        )

    @property
    def reference(self):
        return Reference(
            variable=self.variable,
            index_count=len(self.indices),
        )

    @property
    def dimensions(self):
        return self.variable.dimensions - len(self.indices)

    def is_reference_to(self, variable):
        return self.variable == variable and not self.indices

    def validate_reference(self):
        for expected_index, index_expression in zip_longest(
                reversed(self.context.index_variables),
                reversed(self.indices),
        ):
            if index_expression is None:
                continue

            if expected_index is None:
                yield Diagnostic(
                    Diagnostic.Messages.UNEXPECTED_ARRAY_INDEX,
                    parseinfo=self.ast.parseinfo,
                )
            elif not index_expression.is_reference_to(expected_index.variable):
                yield Diagnostic(
                    Diagnostic.Messages.WRONG_ARRAY_INDEX,
                    expected_index.variable.name,
                    parseinfo=self.ast.parseinfo,
                )

    @property
    def indices(self):
        return tuple(
            Expression.compile(index, self.context)
            for index in self.ast.indices
        )

    def evaluate(self, bindings):
        for index_count in range(self.reference.index_count + 1):
            reference = self.reference._replace(index_count=index_count)
            if reference in bindings:
                return bindings[reference]
        raise AssertionError("reference not bound")

    def validate(self):
        for index in self.indices:
            yield from index.validate_resolved()
        if self.variable_name not in self.context.variable_mapping:
            yield Diagnostic(
                Diagnostic.Messages.VARIABLE_NOT_DECLARED,
                self.variable_name,
                parseinfo=self.ast.parseinfo,
            )


class SyntheticExpression:
    __slots__ = ["expression_type", "__dict__"]

    def __init__(self, expression_type, **kwargs):
        self.expression_type = expression_type
        self.__dict__ = kwargs


expression_classes = frozenbidict({
    "int_literal": IntLiteralExpression,
    "reference": ReferenceExpression,
    "nested": lambda ast, context: Expression.compile(ast.expression, context),
})
