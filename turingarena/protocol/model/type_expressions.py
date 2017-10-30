from abc import abstractmethod

from bidict import bidict

from turingarena.protocol.model.node import TupleLikeObject

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

    @abstractmethod
    def serialize(self, value, *, file):
        pass

    @abstractmethod
    def deserialize(self, *, file):
        pass


@type_expression_class("scalar")
class ScalarType(ValueType):
    __slots__ = ["base_type"]

    @staticmethod
    def compile(ast, scope):
        return ScalarType(
            base_type={"int": int, "bool": bool, }[ast.base_type]
        )

    def serialize(self, value, *, file):
        assert isinstance(value, self.base_type)
        formatters = {
            int: lambda: value,
            bool: lambda: int(value),
        }
        print(formatters[self.base_type](), file=file)

    def deserialize(self, *, file):
        return self.base_type(file.readline().strip())


@type_expression_class("array")
class ArrayType(ValueType):
    __slots__ = ["item_type"]

    @staticmethod
    def compile(ast, scope):
        return ArrayType(
            item_type=ValueType.compile(ast.item_type, scope=scope),
        )

    def serialize(self, value, *, file):
        value = list(value)
        ScalarType(int).serialize(len(value), file=file)
        for item in value:
            self.item_type.deserialize(item, file=file)

    def deserialize(self, *, file):
        size = ScalarType(int).deserialize(file=file)
        return [
            self.item_type.deserialize(file=file)
            for _ in range(size)
        ]
