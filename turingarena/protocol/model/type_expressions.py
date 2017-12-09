from abc import abstractmethod
from bidict import bidict

from turingarena.common import TupleLikeObject

type_expression_classes = bidict()


def type_expression_class(meta_type):
    def decorator(cls):
        type_expression_classes[meta_type] = cls
        return cls

    return decorator


class ValueType(TupleLikeObject):
    __slots__ = ["meta_type"]

    def __init__(self, **kwargs):
        kwargs.setdefault("meta_type", type_expression_classes.inv[self.__class__])
        super().__init__(**kwargs)

    @staticmethod
    def compile(ast, *, scope):
        return type_expression_classes[ast.meta_type].compile(ast, scope)

    def ensure(self, value):
        value = self.intern(value)
        self.check(value)
        return value

    @abstractmethod
    def intern(self, value):
        pass

    @abstractmethod
    def check(self, value):
        pass

    def serialize(self, value):
        yield from self.on_serialize(self.ensure(value))

    @abstractmethod
    def on_serialize(self, value):
        pass

    @abstractmethod
    def deserialize(self, lines):
        pass


class PrimaryType(ValueType):
    __slots__ = []

    def on_serialize(self, value):
        yield self.format(value)

    def deserialize(self, lines):
        return self.parse(next(lines))

    def format(self, value):
        self.check(value)
        return self.do_format(value)

    @abstractmethod
    def do_format(self, value):
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
        }
        return ScalarType(bases[ast.base_type])

    def intern(self, value):
        return value

    def check(self, value):
        if not isinstance(value, self.base_type):
            raise TypeError(f"expected a {self.base_type}, got {value}")

    def do_format(self, value):
        formatters = {
            int: lambda: value,
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
        for x in value:
            self.item_type.check(x)

    def on_serialize(self, value):
        value = list(value)
        yield from ScalarType(int).serialize(len(value))
        for item in value:
            yield from self.item_type.serialize(item)

    def deserialize(self, lines):
        size = ScalarType(int).deserialize(lines)
        return [
            self.item_type.deserialize(lines)
            for _ in range(size)
        ]
