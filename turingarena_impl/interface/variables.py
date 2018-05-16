from abc import abstractmethod
from collections import namedtuple

from turingarena_impl.interface.common import AbstractSyntaxNodeWrapper

VariableDeclaration = namedtuple("VariableDeclaration", ["name", "dimensions", "to_allocate"])
VariableAllocation = namedtuple("VariableAllocation", ["name", "dimensions", "indexes", "size"])


class Variable(namedtuple("Variable", ["name", "value_type"])):
    pass


class TypeExpression(AbstractSyntaxNodeWrapper):
    @staticmethod
    def value_type_dimensions(dimensions):
        if not dimensions:
            return ScalarType()
        if type(dimensions) is int:
            return ArrayType(TypeExpression.value_type_dimensions(dimensions - 1))
        return ArrayType(TypeExpression.value_type_dimensions(dimensions[1:]))


class ValueType:
    __slots__ = []

    @property
    @abstractmethod
    def meta_type(self):
        pass


class ScalarType(ValueType):
    __slots__ = []

    def __str__(self):
        return "scalar"

    @property
    def meta_type(self):
        return "scalar"


class ArrayType(ValueType, namedtuple("ArrayType", ["item_type"])):
    __slots__ = []

    def __str__(self):
        return f"{self.item_type}[]"

    @property
    def dimensions(self):
        dimensions = 0
        item_type = self
        while item_type.meta_type == 'array':
            dimensions += 1
            item_type = item_type.item_type
        return dimensions

    @property
    def meta_type(self):
        return "array"
