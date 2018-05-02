import logging

from abc import abstractmethod
from collections import namedtuple

from turingarena_impl.interface.node import AbstractSyntaxNodeWrapper

logger = logging.getLogger(__name__)


def compile_type_expression(ast, context):
    return TypeExpression(ast, context)


class TypeExpression(AbstractSyntaxNodeWrapper):
    @staticmethod
    def value_type_dimensions(dimensions):
        if not dimensions:
            return ScalarType(int)
        return ArrayType(TypeExpression.value_type_dimensions(dimensions[1:]))

    @property
    def value_type(self):
        if self.ast.prototype:
            return CallbackType.compile(self.ast.prototype)
        return self.value_type_dimensions(self.ast.indexes)


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

    @property
    def metadata_attributes(self):
        return dict(base_type=str(self.base_type))


class ArrayType(ValueType, namedtuple("ArrayType", ["item_type"])):
    __slots__ = []

    def __str__(self):
        return f"{self.item_type}[]"

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


class CallbackType(ValueType, namedtuple("CallbackType", ["number_of_arguments", "has_return_value"])):
    @staticmethod
    def compile(ast):
        return CallbackType(
            number_of_arguments=len(ast.parameters),
            has_return_value=ast.return_type == "int",
        )

    @property
    def meta_type(self):
        return "callback"

    def __str__(self):
        return f"{'int' if self.has_return_value else 'void' } ({', '.join(['int' for _ in range(self.number_of_arguments)])})"
