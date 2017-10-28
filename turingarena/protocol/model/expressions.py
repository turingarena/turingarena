from bidict import bidict

from turingarena.protocol.model.node import AbstractSyntaxNode
from turingarena.protocol.model.type_expressions import ScalarType

expression_classes = bidict()


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


@expression_class("int_literal")
class IntLiteralExpression(Expression):
    __slots__ = ["int_value"]

    @staticmethod
    def compile(ast, scope):
        return IntLiteralExpression(
            int_value=int(ast.int_literal),
            value_type=ScalarType(int),
        )


@expression_class("bool_literal")
class BoolLiteralExpression(Expression):
    __slots__ = ["bool_value"]

    @staticmethod
    def compile(ast, scope):
        return IntLiteralExpression(
            bool_value=bool(int(ast.int_literal)),
            value_type=ScalarType(bool),
        )


@expression_class("reference")
class ReferenceExpression(Expression):
    __slots__ = ["variable"]

    @staticmethod
    def compile(ast, scope):
        variable = scope["var", ast.variable_name]
        return ReferenceExpression(
            variable=variable,
            value_type=variable.type,
        )


@expression_class("subscript")
class SubscriptExpression(Expression):
    __slots__ = ["array", "index"]

    @staticmethod
    def compile(ast, scope):
        array = Expression.compile(ast.array, scope=scope)
        index = Expression.compile(ast.index, scope=scope, expected_type=ScalarType(base_type=int))
        return SubscriptExpression(
            array=array,
            index=index,
            value_type=array.value_type.item_type,
        )
