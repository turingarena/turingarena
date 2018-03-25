import logging
from abc import abstractmethod

from bidict import frozenbidict

from turingarena.interface.exceptions import VariableNotInitializedError, \
    VariableNotDeclaredError
from turingarena.interface.node import AbstractSyntaxNodeWrapper
from turingarena.interface.references import ConstantReference, VariableReference, ArrayItemReference
from turingarena.interface.type_expressions import ScalarType

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
            raise VariableNotDeclaredError(f"Variable {self.variable_name} is not declared")

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

    def check_variables(self, initialized_variables, allocated_variables):
        if self.variable not in initialized_variables:
            raise VariableNotInitializedError(f"Variable '{self.variable.name}' used before initialization")
        for index in self.indices:
            index.check_variables(initialized_variables, allocated_variables)

    def resolve_variable(self):
        return self.variable


expression_classes = frozenbidict({
    "int_literal": IntLiteralExpression,
    "reference": ReferenceExpression,
})
