import logging
from abc import abstractmethod
from collections import namedtuple

from turingarena_impl.interface.variables import ScalarType, ArrayType

logger = logging.getLogger(__name__)


class Reference:
    __slots__ = []

    @property
    @abstractmethod
    def value_type(self):
        pass

    def get(self):
        assert self.is_resolved()
        return self.do_get()

    def is_resolved(self):
        return self.do_get() is not None

    def resolve(self, value):
        value = self.value_type.ensure(value)
        previous_value = self.do_get()
        if previous_value is None:
            self.do_set(value)
        else:
            assert value == previous_value

    def alloc(self, size):
        assert isinstance(self.value_type, ArrayType)
        previous_value = self.do_get()
        if previous_value is None:
            self.do_set([None] * size)
        else:
            assert len(previous_value) == size

    @abstractmethod
    def do_get(self):
        pass

    @abstractmethod
    def do_set(self, value):
        pass


class ConstantReference(Reference, namedtuple("ConstantReference", [
    "value_type", "value"
])):
    __slots__ = []

    @property
    def value_type(self):
        return self.value_type

    def validate(self):
        # TODO: never called
        assert isinstance(self.value_type, ScalarType)
        self.value_type.check(self.value)

    def do_get(self):
        return self.value

    def do_set(self, value):
        pass


class VariableReference(Reference, namedtuple("VariableReference", [
    "context", "variable"
])):
    __slots__ = []

    @property
    def value_type(self):
        return self.variable.value_type

    def do_get(self):
        return self.context.bindings[self.variable.name]

    def do_set(self, value):
        self.context.bindings[self.variable.name] = value

    def __str__(self):
        return f"var({self.variable.name})"


# FIXME: merge VariableReference and ArrayItemReference (using a tuple of indices?)
class ArrayItemReference(Reference, namedtuple("ArrayItemReference", [
    "array_type", "array", "index"
])):
    __slots__ = []

    @property
    def value_type(self):
        return self.array_type.item_type

    def validate(self):
        assert isinstance(self.index, int)
        assert isinstance(self.array, list)

    def do_get(self):
        return self.array[self.index]

    def do_set(self, value):
        self.array[self.index] = value

    def __str__(self):
        return f"item({self.array}, {self.index})"
