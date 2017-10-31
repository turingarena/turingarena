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

    def ensure(self, value):
        value = self.intern(value)
        assert self.check(value)
        return value

    @abstractmethod
    def intern(self, value):
        pass

    @abstractmethod
    def check(self, value):
        pass

    def serialize(self, value, *, file):
        return self.on_serialize(self.ensure(value), file=file)

    @abstractmethod
    def on_serialize(self, value, *, file):
        pass

    @abstractmethod
    def deserialize(self, *, file):
        pass


class PrimaryType(ValueType):
    __slots__ = []

    def on_serialize(self, value, *, file):
        print(self.format(value), file=file)

    def deserialize(self, *, file):
        return self.parse(file.readline().strip())

    @abstractmethod
    def format(self, value):
        pass

    @abstractmethod
    def parse(self, string):
        pass


@type_expression_class("scalar")
class ScalarType(PrimaryType):
    __slots__ = ["base_type"]

    def __init__(self, base_type):
        super().__init__(base_type=base_type)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.base_type.__name__})"

    @staticmethod
    def compile(ast, scope):
        bases = {
            "int": int,
            "bool": bool,
        }
        return ScalarType(bases[ast.base_type])

    def intern(self, value):
        return value

    def check(self, value):
        assert isinstance(value, self.base_type)

    def format(self, value):
        formatters = {
            int: lambda: value,
            bool: lambda: int(value),
        }
        return formatters[self.base_type]()

    def parse(self, string):
        return self.base_type(string)


@type_expression_class("array")
class ArrayType(ValueType):
    __slots__ = ["item_type"]

    @staticmethod
    def compile(ast, scope):
        return ArrayType(
            item_type=ValueType.compile(ast.item_type, scope=scope),
        )

    def intern(self, value):
        return [
            self.item_type.ensure(x)
            for x in value
        ]

    def check(self, value):
        assert type(value) == list
        assert all(self.item_type.check(x) for x in value)

    def on_serialize(self, value, *, file):
        value = list(value)
        ScalarType(int).on_serialize(len(value), file=file)
        for item in value:
            self.item_type.deserialize(item, file=file)

    def deserialize(self, *, file):
        size = ScalarType(int).deserialize(file=file)
        return [
            self.item_type.deserialize(file=file)
            for _ in range(size)
        ]
