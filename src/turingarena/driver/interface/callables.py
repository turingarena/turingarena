import logging
from collections import namedtuple

from turingarena.driver.interface.variables import Variable

logger = logging.getLogger(__name__)


class ParameterDeclaration(namedtuple("ParameterDeclaration", ["ast"])):
    __slots__ = []

    @property
    def variable(self):
        return Variable(
            name=self.ast.name,
        )

    @property
    def dimensions(self):
        return len(self.ast.indexes)


class CallablePrototype(namedtuple("CallablePrototype", ["ast", "description"])):
    __slots__ = []

    @property
    def name(self):
        return self.ast.declarator.name

    @property
    def parameter_declarations(self):
        return [
            ParameterDeclaration(ast=p)
            for p in self.ast.declarator.parameters
        ]

    @property
    def parameters(self):
        return [
            p.variable
            for p in self.parameter_declarations
        ]

    @property
    def has_return_value(self):
        return self.ast.declarator.type == 'function'

    @property
    def callbacks(self):
        return [
            CallbackPrototype(callback, description=None)
            for callback in self.ast.callbacks
        ]

    @property
    def has_callbacks(self):
        return bool(self.callbacks)


class MethodPrototype(CallablePrototype):
    __slots__ = []


class CallbackPrototype(CallablePrototype):
    __slots__ = []
