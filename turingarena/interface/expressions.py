import logging
from abc import abstractmethod
from collections import namedtuple

from bidict import bidict

from turingarena.interface.exceptions import VariableNotAllocatedError, VariableNotInitializedError, \
    VariableNotDeclaredError
from turingarena.interface.references import ConstantReference, VariableReference, ArrayItemReference
from turingarena.interface.type_expressions import ScalarType

expression_classes = bidict()

logger = logging.getLogger(__name__)


def expression_class(meta_type):
    def decorator(cls):
        expression_classes[meta_type] = cls
        return cls

    return decorator


def compile_expression(ast, context):
    return expression_classes[ast.expression_type](ast=ast, context=context)


class Expression(namedtuple("Expression", ["ast", "context"])):
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


@expression_class("int_literal")
class IntLiteralExpression(LiteralExpression):
    __slots__ = []

    @property
    def value(self):
        return int(self.ast.int_literal)

    @property
    def value_type(self):
        return ScalarType(int)


@expression_class("reference")
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
    def value_type(self):
        return self.variable.value_type

    def do_evaluate(self, context):
        return VariableReference(
            context=context,
            variable=self.variable,
            value_type=self.value_type,
        )

    def check_variables(self, initialized_variables, allocated_variables):
        if self.variable not in initialized_variables:
            raise VariableNotInitializedError(f"Variable '{self.variable.name}' used before initialization")

    def resolve_variable(self):
        return self.variable


@expression_class("subscript")
class SubscriptExpression(Expression):
    __slots__ = []

    @property
    def array(self):
        return compile_expression(self.ast.array, self.context)

    @property
    def index(self):
        return compile_expression(self.ast.index, self.context)

    def do_evaluate(self, context):
        return ArrayItemReference(
            value_type=self.array.value_type.item_type,
            array=self.array.evaluate_in(context).get(),
            index=self.index.evaluate_in(context).get(),
        )

    @property
    def value_type(self):
        return self.array.value_type.item_type

    def check_variables(self, initialized_variables, allocated_variables):
        if self.array.variable not in allocated_variables:
            raise VariableNotAllocatedError(f"Variable '{self.array.resolve_variable().name}' used before allocation")
        self.index.check_variables(initialized_variables, allocated_variables)
        self.array.check_variables(initialized_variables, allocated_variables)

    def resolve_variable(self):
        return self.array.resolve_variable()
