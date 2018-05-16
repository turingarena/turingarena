import logging
from abc import abstractmethod

from bidict import frozenbidict

from turingarena_impl.interface.common import AbstractSyntaxNodeWrapper
from turingarena_impl.interface.exceptions import Diagnostic
from turingarena_impl.interface.variables import ScalarType

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

    def is_assignable(self):
        return False

    def assign(self, bindings, value):
        raise NotImplementedError

    def alloc(self, bindings, size):
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
        value = bindings[self.variable.name]
        for index in self.indices:
            assert value is not None
            value = value[index.evaluate(bindings)]
        assert value is not None
        return value

    def is_assignable(self):
        return True

    def assign(self, bindings, value):
        # TODO: handle indices
        bindings[self.variable.name] = value

    def alloc(self, bindings, size):
        # TODO: handle indices
        bindings[self.variable.name] = [None] * size

    def validate(self, lvalue=False):
        last_index = 0
        index_var = {index.variable: index.range for index in self.context.index_variables}
        for index in self.indices:
            if isinstance(index, LiteralExpression):
                yield Diagnostic(Diagnostic.Messages.ARRAY_INDEX_NOT_VALID, index.value, parseinfo=self.ast.parseinfo)
            else:
                idx = 0
                try:
                    idx = list(index_var).index(index.variable)
                except ValueError:
                    yield Diagnostic(Diagnostic.Messages.ARRAY_INDEX_NOT_VALID, index.variable_name,
                                     parseinfo=self.ast.parseinfo)
                if idx < last_index:
                    yield Diagnostic(Diagnostic.Messages.ARRAY_INDEX_WRONG_ORDER, self.variable_name,
                                     parseinfo=self.ast.parseinfo)
                last_index = idx


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
