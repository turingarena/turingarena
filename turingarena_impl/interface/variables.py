from abc import abstractmethod
from collections import namedtuple

VariableDeclaration = namedtuple("VariableDeclaration", ["name", "dimensions", "to_allocate"])
VariableAllocation = namedtuple("VariableAllocation", ["name", "dimensions", "indexes", "size"])


class Variable(namedtuple("Variable", ["name", "value_type"])):
    @staticmethod
    def value_type_dimensions(dimensions):
        if not dimensions:
            return ScalarType()
        if type(dimensions) is int:
            return ArrayType(Variable.value_type_dimensions(dimensions - 1))
        return ArrayType(Variable.value_type_dimensions(dimensions[1:]))


class ValueType:
    __slots__ = []

    @property
    @abstractmethod
    def meta_type(self):
        pass

    @property
    @abstractmethod
    def dimensions(self):
        pass


class ScalarType(ValueType):
    __slots__ = []

    def __str__(self):
        return "scalar"

    @property
    def meta_type(self):
        return "scalar"

    @property
    def dimensions(self):
        return 0


class ArrayType(ValueType, namedtuple("ArrayType", ["item_type"])):
    __slots__ = []

    def __str__(self):
        return f"{self.item_type}[]"

    @property
    def dimensions(self):
        return self.item_type.dimensions + 1

    @property
    def meta_type(self):
        return "array"
