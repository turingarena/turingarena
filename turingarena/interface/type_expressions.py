from abc import abstractmethod

from bidict import bidict

from turingarena.common import TupleLikeObject


class ValueType(TupleLikeObject):
    __slots__ = ["meta_type"]

    def __init__(self, **kwargs):
        kwargs.setdefault("meta_type", type_expression_classes.inv[self.__class__])
        super().__init__(**kwargs)

    @staticmethod
    def compile(ast):
        return type_expression_classes[ast.meta_type].do_compile(ast)

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

    @property
    def metadata(self):
        return dict(
            meta_type=self.meta_type,
            **self.metadata_attributes
        )

    @property
    @abstractmethod
    def metadata_attributes(self):
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


class ScalarType(PrimaryType):
    __slots__ = ["base_type"]

    def __init__(self, base_type):
        super().__init__(base_type=base_type)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.base_type.__name__})"

    def __str__(self):
        return self.base_type.__name__

    @staticmethod
    def do_compile(ast):
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

    @property
    def metadata_attributes(self):
        return dict(base_type=str(self.base_type))


class ArrayType(ValueType):
    __slots__ = ["item_type"]

    @staticmethod
    def do_compile(ast):
        return ArrayType(
            item_type=ValueType.compile(ast.item_type),
        )

    def __str__(self):
        return f"{self.item_type}[]"

    @property
    def metadata_attributes(self):
        return dict(item_type=self.item_type.metadata)

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
            self.item_type.deserialize_arguments(lines)
            for _ in range(size)
        ]


type_expression_classes = bidict({
    "scalar": ScalarType,
    "array": ArrayType,
})
