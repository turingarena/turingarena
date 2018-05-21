import logging
from abc import abstractmethod
from itertools import zip_longest

from bidict import frozenbidict

from turingarena_impl.interface.common import AbstractSyntaxNodeWrapper
from turingarena_impl.interface.diagnostics import Diagnostic
from turingarena_impl.interface.variables import ScalarType, DataReference

logger = logging.getLogger(__name__)


class Expression(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @staticmethod
    def compile(ast, context):
        return expression_classes[ast.expression_type](ast, context)

    @property
    def expression_type(self):
        return self.ast.expression_type

    @property
    @abstractmethod
    def value_type(self):
        pass

    @abstractmethod
    def evaluate(self, bindings):
        pass

    def is_scalar_reference_to(self, variable):
        return False

    def is_assignable(self):
        return False

    def assign(self, bindings, value):
        raise NotImplementedError

    def validate(self):
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
    def canonical_form(self):
        return self.value

    @property
    def value(self):
        return int(self.ast.int_literal)

    @property
    def value_type(self):
        return ScalarType()


class ReferenceExpression(Expression):
    __slots__ = []

    @property
    def variable_name(self):
        return self.ast.variable_name

    @property
    def variable(self):
        return self.context.variable_mapping[self.variable_name]

    @property
    def reference(self):
        return DataReference(
            variable=self.variable,
            indexes=tuple(None for _ in self.indices),
        )

    def is_scalar_reference_to(self, variable):
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
            elif not index_expression.is_scalar_reference_to(expected_index):
                yield Diagnostic(
                    Diagnostic.Messages.WRONG_ARRAY_INDEX,
                    expected_index.name,
                    parseinfo=self.ast.parseinfo,
                )

    @property
    def value_type(self):
        if self.variable:
            value_type = self.variable.value_type
        else:
            value_type = ScalarType()
        for _ in self.indices:
            value_type = value_type.item_type
        return value_type

    @property
    def indices(self):
        return tuple(
            Expression.compile(index, self.context)
            for index in self.ast.indices
        )

    def evaluate(self, bindings):
        value = self.get_reference(bindings).get()
        assert value is not None
        return value

    def is_assignable(self):
        return True

    def assign(self, bindings, value):
        self.get_reference(bindings).set(value)

    def validate(self):
        return []


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
