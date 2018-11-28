import logging
from collections import namedtuple

logger = logging.getLogger(__name__)


class ParameterDeclaration(namedtuple("ParameterDeclaration", ["variable", "dimensions"])):
    __slots__ = []


class CallablePrototype(namedtuple("CallablePrototype", [
    "name",
    "parameter_declarations",
    "has_return_value",
    "callbacks",
])):
    __slots__ = []

    @property
    def parameters(self):
        return [
            p.variable
            for p in self.parameter_declarations
        ]

    @property
    def has_callbacks(self):
        return bool(self.callbacks)


class MethodPrototype(CallablePrototype):
    __slots__ = []


class CallbackPrototype(CallablePrototype):
    __slots__ = []
