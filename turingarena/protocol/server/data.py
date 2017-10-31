import logging
from abc import abstractmethod

from turingarena.protocol.model.node import ImmutableObject
from turingarena.protocol.model.type_expressions import PrimaryType, ArrayType

logger = logging.getLogger(__name__)


class Reference(ImmutableObject):
    __slots__ = ["value_type"]

    def get(self):
        value = self.do_get()
        assert value is not None
        return value

    def resolve(self, value):
        logger.debug(f"resolving {self} <- {value}")
        value = self.value_type.ensure(value)
        previous_value = self.do_get()
        if previous_value is None:
            logger.debug(f"resolving: setting {self} <- {value}")
            self.do_set(value)
        else:
            logger.debug(f"resolving: checking {self} == {value}")
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


class ConstantReference(Reference):
    __slots__ = ["value"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        assert isinstance(self.value_type, PrimaryType)
        self.value_type.check(self.value)

    def do_get(self):
        return self.value

    def do_set(self, value):
        pass


class VariableReference(Reference):
    __slots__ = ["frame", "variable"]

    def do_get(self):
        return self.frame[self.variable]

    def do_set(self, value):
        self.frame[self.variable] = value

    def __str__(self):
        return f"var({self.variable.name})"


class ArrayItemReference(Reference):
    __slots__ = ["array", "index"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        assert isinstance(self.index, int)
        assert isinstance(self.array, list)

    def do_get(self):
        return self.array[self.index]

    def do_set(self, value):
        self.array[self.index] = value

    def __str__(self):
        return f"item({self.array}, {self.index})"
