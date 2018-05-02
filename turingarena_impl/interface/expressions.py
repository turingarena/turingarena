from abc import abstractmethod

from bidict import frozenbidict

from turingarena_impl.interface.exceptions import Diagnostic
from turingarena_impl.interface.node import AbstractSyntaxNodeWrapper
from turingarena_impl.interface.references import ConstantReference, VariableReference, ArrayItemReference
from turingarena_impl.interface.type_expressions import ScalarType, ArrayType

import logging

logger = logging.getLogger(__name__)


class Expression(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @staticmethod
    def compile(ast, context):
        return expression_classes[ast.expression_type](ast, context)

    @property
    def expression_type(self):
        return expression_classes.inv[self.__class__]

    @property
    @abstractmethod
    def value_type(self):
        pass

    def evaluate_in(self, context):
        return self.do_evaluate(context)

    @abstractmethod
    def do_evaluate(self, context):
        pass

    @property
    @abstractmethod
    def canonical_form(self):
        pass

    def validate(self):
        return []


class LiteralExpression(Expression):
    __slots__ = []

    @property
    @abstractmethod
    def value(self):
        pass

    def do_evaluate(self, context):
        return ConstantReference(
            value_type=self.value_type,
            value=self.value,
        )


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
        return ScalarType(int)


class ReferenceExpression(Expression):
    __slots__ = []

    @property
    def canonical_form(self):
        return self.variable_name

    @property
    def variable_name(self):
        return self.ast.variable_name

    @property
    def variable(self):
        try:
            return self.context.variable_mapping[self.variable_name]
        except KeyError:
            return None

    @property
    def indices(self):
        logger.debug(f"{self.ast}")
        return tuple(
            Expression.compile(index, self.context)
            for index in self.ast.indices
        )

    @property
    def value_type(self):
        if self.variable:
            value_type = self.variable.value_type
        else:
            value_type = ScalarType(int)
        for _ in self.indices:
            value_type = value_type.item_type
        return value_type

    def do_evaluate(self, context):
        ref = VariableReference(
            context=context,
            variable=self.variable,
        )
        for index in self.indices:
            ref = ArrayItemReference(
                array_type=ref.value_type,
                array=ref.get(),
                index=index.evaluate_in(context).get(),
            )
        return ref

    def validate_array_indexes(self):
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

    def validate(self, lvalue=False):
        if not lvalue and self.variable_name not in self.context.variable_mapping:
            yield Diagnostic(Diagnostic.Messages.VARIABLE_NOT_DECLARED, self.variable_name,
                             parseinfo=self.ast.parseinfo)

        #if isinstance(self.variable.value_type, ArrayType):
        #    for index in self.indices:
        #        yield from index.validate()
        #    if lvalue:
        #        yield from self.validate_array_indexes()


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
