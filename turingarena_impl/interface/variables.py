from abc import abstractmethod
from collections import namedtuple

from turingarena_impl.interface.common import AbstractSyntaxNodeWrapper

VariableDeclaration = namedtuple("VariableDeclaration", ["name", "dimensions", "to_allocate"])
VariableAllocation = namedtuple("VariableAllocation", ["name", "dimensions", "indexes", "size"])


class Variable(namedtuple("Variable", ["name", "value_type"])):
    @property
    def metadata(self):
        return dict(
            name=self.name,
            type=self.value_type.metadata,
        )


class TypeExpression(AbstractSyntaxNodeWrapper):
    @staticmethod
    def value_type_dimensions(dimensions):
        if not dimensions:
            return ScalarType()
        if type(dimensions) is int:
            return ArrayType(TypeExpression.value_type_dimensions(dimensions - 1))
        return ArrayType(TypeExpression.value_type_dimensions(dimensions[1:]))

    @property
    def value_type(self):
        if self.ast.prototype:
            return CallbackType.compile(self.ast.prototype)
        return self.value_type_dimensions(self.ast.indexes)


class ValueType:
    __slots__ = []

    def __eq__(self, other):
        return str(self) == str(other)

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


class ScalarType(ValueType):
    __slots__ = []

    def __str__(self):
        return "int"

    @property
    def meta_type(self):
        return "scalar"

    def intern(self, value):
        return value

    def check(self, value):
        if not isinstance(value, int):
            raise TypeError(f"expected a int, got {value}")

    @property
    def metadata_attributes(self):
        return dict(base_type=str(self.base_type))


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


class CallbackType(ValueType, namedtuple("CallbackType", ["arguments", "has_return_value"])):
    __slots__ = []

    @staticmethod
    def compile(ast):
        return CallbackType(
            arguments=tuple(p.name for p in ast.parameters),
            has_return_value=ast.return_type == "int",
        )

    @property
    def number_of_arguments(self):
        return len(self.arguments)

    @property
    def meta_type(self):
        return "callback"

    def __str__(self):
        return f"{'int' if self.has_return_value else 'void'} ({', '.join([f'int' for a in self.arguments])})"
