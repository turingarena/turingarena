from bidict import bidict

from turingarena.protocol.model.node import ImmutableObject, TupleLikeObject

type_expression_classes = bidict()


def type_expression_class(meta_type):
    def decorator(cls):
        type_expression_classes[meta_type] = cls
        return cls

    return decorator


class ValueType(TupleLikeObject):
    __slots__ = ["meta_type"]

    def __init__(self, **kwargs):
        super().__init__(meta_type=type_expression_classes.inv[self.__class__], **kwargs)

    @staticmethod
    def compile(ast, *, scope):
        return type_expression_classes[ast.meta_type].compile(ast, scope)


@type_expression_class("scalar")
class ScalarType(ValueType):
    __slots__ = ["base_type"]

    @staticmethod
    def compile(ast, scope):
        return ScalarType(
            base_type={"int": int, "bool": bool, }[ast.base_type]
        )


@type_expression_class("array")
class ArrayType(ValueType):
    __slots__ = ["item_type"]

    @staticmethod
    def compile(ast, scope):
        return ArrayType(
            item_type=ValueType.compile(ast.item_type, scope=scope),
        )
