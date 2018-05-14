from abc import abstractmethod
from collections import namedtuple

from turingarena_impl.interface.node import AbstractSyntaxNodeWrapper


def compile_type_expression(ast, context):
    return TypeExpression(ast, context)


class TypeExpression(AbstractSyntaxNodeWrapper):
    def value_type_dimensions(self, dimensions):
        if not dimensions:
            return ScalarType(int)
        return ArrayType(self.value_type_dimensions(dimensions[1:]))

    @property
    def value_type(self):
        return self.value_type_dimensions(self.ast.dimensions)


class ValueType:
    __slots__ = []

    @property
    @abstractmethod
    def meta_type(self):
        pass

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


class ScalarType(ValueType, namedtuple("ScalarType", ["base_type"])):
    __slots__ = []

    def __str__(self):
        return self.base_type.__name__

    @property
    def meta_type(self):
        return "scalar"

    def intern(self, value):
        return value

    def check(self, value):
        if not isinstance(value, self.base_type):
            raise TypeError(f"expected a {self.base_type}, got {value}")


class ArrayType(ValueType, namedtuple("ArrayType", ["item_type"])):
    __slots__ = []

    def __str__(self):
        return f"{self.item_type}[]"

    @property
    def meta_type(self):
        return "array"

    def intern(self, value):
        return [
            self.item_type.ensure(x)
            for x in value
        ]

    def check(self, value):
        assert type(value) == list
        for x in value:
            self.item_type.check(x)
