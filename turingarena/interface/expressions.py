import logging
from abc import abstractmethod

from bidict import frozenbidict

from turingarena.interface.exceptions import Diagnostic
from turingarena.interface.node import AbstractSyntaxNodeWrapper
from turingarena.interface.references import ConstantReference, VariableReference, ArrayItemReference
from turingarena.interface.type_expressions import ScalarType, ArrayType

logger = logging.getLogger(__name__)


def compile_expression(ast, context):
    return expression_classes[ast.expression_type](ast=ast, context=context)


class Expression(AbstractSyntaxNodeWrapper):
    __slots__ = []

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

    def resolve_variable(self):
        return None

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
    def value(self):
        return int(self.ast.int_literal)

    @property
    def value_type(self):
        return ScalarType(int)


class ReferenceExpression(Expression):
    __slots__ = []

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
        return tuple(
            compile_expression(index, self.context)
            for index in self.ast.indices
        )

    @property
    def value_type(self):
        value_type = self.variable.value_type
        for i in self.indices:
            value_type = value_type.item_type
        return value_type

    def do_evaluate(self, context):
        ref = VariableReference(
            context=context,
            variable=self.variable,
            value_type=self.variable.value_type,
        )
        for index in self.indices:
            ref = ArrayItemReference(
                value_type=ref.value_type.item_type,
                array=ref.get(),
                index=index.evaluate_in(context).get(),
            )
        return ref

    def validate(self, lvalue=False):
        if not self.variable:
            yield Diagnostic("variable a not declared")
        elif self.variable not in self.context.initialized_variables and not lvalue:
            yield Diagnostic(f"variable {self.variable.name} used before initialization")
        elif isinstance(self.variable.value_type, ArrayType):
            if self.variable not in self.context.allocated_variables:
                yield Diagnostic(f"variable {self.variable.name} used before allocation")
            for index in self.indices:
                yield from index.validate()

    def resolve_variable(self):
        return self.variable


expression_classes = frozenbidict({
    "int_literal": IntLiteralExpression,
    "reference": ReferenceExpression,
})
