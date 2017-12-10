import logging
from abc import abstractmethod

from bidict import bidict

from turingarena.protocol.model.node import AbstractSyntaxNode
from turingarena.protocol.model.type_expressions import ScalarType
from turingarena.protocol.server.references import ConstantReference, VariableReference, ArrayItemReference

expression_classes = bidict()

logger = logging.getLogger(__name__)


def expression_class(meta_type):
    def decorator(cls):
        expression_classes[meta_type] = cls
        return cls

    return decorator


class Expression(AbstractSyntaxNode):
    __slots__ = ["expression_type", "value_type"]

    def __init__(self, **kwargs):
        super().__init__(expression_type=expression_classes.inv[self.__class__], **kwargs)

    @staticmethod
    def compile(ast, *, scope, expected_type=None):
        expression = expression_classes[ast.expression_type].compile(ast, scope)
        actual_type = expression.value_type
        if expected_type and actual_type != expected_type:
            raise ValueError("expected {}, got {}".format(expected_type, actual_type))
        return expression

    def evaluate(self, *, frame):
        logger.debug(f"evaluating expression {self} in {frame}")
        return self.do_evaluate(frame=frame)

    @abstractmethod
    def do_evaluate(self, *, frame):
        pass


class LiteralExpression(Expression):
    __slots__ = ["value"]

    def do_evaluate(self, *, frame):
        return ConstantReference(
            value_type=self.value_type,
            value=self.value,
        )


@expression_class("int_literal")
class IntLiteralExpression(LiteralExpression):
    __slots__ = []

    @staticmethod
    def compile(ast, scope):
        return IntLiteralExpression(
            value_type=ScalarType(int),
            value=int(ast.int_literal),
        )


@expression_class("reference")
class ReferenceExpression(Expression):
    __slots__ = ["variable"]

    @staticmethod
    def compile(ast, scope):
        variable = scope.variables[ast.variable_name]
        return ReferenceExpression(
            value_type=variable.value_type,
            variable=variable,
        )

    def do_evaluate(self, *, frame):
        return VariableReference(
            frame=frame,
            variable=self.variable,
        )


@expression_class("subscript")
class SubscriptExpression(Expression):
    __slots__ = ["array", "index"]

    @staticmethod
    def compile(ast, scope):
        array = Expression.compile(ast.array, scope=scope)
        index = Expression.compile(ast.index, scope=scope, expected_type=ScalarType(int))
        return SubscriptExpression(
            array=array,
            index=index,
            value_type=array.value_type.item_type,
        )

    def do_evaluate(self, *, frame):
        return ArrayItemReference(
            value_type=self.array.value_type.item_type,
            array=self.array.evaluate(frame=frame).get(),
            index=self.index.evaluate(frame=frame).get(),
        )
