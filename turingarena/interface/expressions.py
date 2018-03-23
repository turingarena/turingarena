import logging
from abc import abstractmethod

from bidict import bidict

from turingarena.interface.exceptions import VariableNotAllocatedError, VariableNotInitializedError, \
    VariableNotDeclaredError
from turingarena.interface.node import AbstractSyntaxNode
from turingarena.interface.references import ConstantReference, VariableReference, ArrayItemReference
from turingarena.interface.type_expressions import ScalarType

expression_classes = bidict()

logger = logging.getLogger(__name__)


def expression_class(meta_type):
    def decorator(cls):
        expression_classes[meta_type] = cls
        return cls

    return decorator


class Expression(AbstractSyntaxNode):
    __slots__ = ["ast"]

    @staticmethod
    def compile(ast):
        return expression_classes[ast.expression_type].do_compile(ast)

    @property
    def expression_type(self):
        return expression_classes.inv[self.__class__]

    @abstractmethod
    def value_type(self, *, declared_variables):
        pass

    def evaluate_in(self, context):
        return self.do_evaluate(context)

    @abstractmethod
    def do_evaluate(self, context):
        pass

    def resolve_variable(self):
        return None


class LiteralExpression(Expression):
    __slots__ = ["value"]

    def do_evaluate(self, context):
        return ConstantReference(
            value_type=self.value_type,
            value=self.value,
        )


@expression_class("int_literal")
class IntLiteralExpression(LiteralExpression):
    __slots__ = []

    @staticmethod
    def do_compile(ast):
        return IntLiteralExpression(
            ast=ast,
            value=int(ast.int_literal),
        )

    def value_type(self, *, declared_variables):
        return ScalarType(int)


@expression_class("reference")
class ReferenceExpression(Expression):
    __slots__ = []

    @staticmethod
    def do_compile(ast):
        return ReferenceExpression(
            ast=ast,
        )

    @property
    def variable_name(self):
        return self.ast.variable_name

    def variable(self, *, declared_variables):
        try:
            return declared_variables[self.variable_name]
        except KeyError:
            raise VariableNotDeclaredError(f"Variable {self.variable_name} is not declared")

    def value_type(self, *, declared_variables):
        return self.variable(declared_variables=declared_variables).value_type

    def do_evaluate(self, context):
        value_type = self.value_type(declared_variables=context.variables)
        return VariableReference(
            context=context,
            variable=self.variable(declared_variables=context.variables),
            value_type=value_type,
        )

    def check_variables(self, initialized_variables, allocated_variables):
        if self.variable not in initialized_variables:
            raise VariableNotInitializedError(f"Variable '{self.variable.name}' used before initialization")

    def resolve_variable(self):
        return self.variable


@expression_class("subscript")
class SubscriptExpression(Expression):
    __slots__ = ["array", "index"]

    @staticmethod
    def do_compile(ast):
        array = Expression.compile(ast.array)
        index = Expression.compile(ast.index)
        return SubscriptExpression(
            ast=ast,
            array=array,
            index=index,
        )

    def do_evaluate(self, context):
        return ArrayItemReference(
            value_type=self.array.value_type(declared_variables=context.variables).item_type,
            array=self.array.evaluate_in(context).get(),
            index=self.index.evaluate_in(context).get(),
        )

    def value_type(self, *, declared_variables):
        return self.array.value_type(declared_variables=declared_variables).item_type

    def check_variables(self, initialized_variables, allocated_variables):
        if self.array.variable not in allocated_variables:
            raise VariableNotAllocatedError(f"Variable '{self.array.resolve_variable().name}' used before allocation")
        self.index.check_variables(initialized_variables, allocated_variables)
        self.array.check_variables(initialized_variables, allocated_variables)

    def resolve_variable(self):
        return self.array.resolve_variable()
