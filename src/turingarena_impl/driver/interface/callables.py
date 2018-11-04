import logging
from collections import namedtuple

from turingarena_impl.driver.interface.common import AbstractSyntaxNodeWrapper
from turingarena_impl.driver.interface.diagnostics import Diagnostic
from turingarena_impl.driver.interface.variables import Variable

logger = logging.getLogger(__name__)


class ParameterDeclaration(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def variable(self):
        return Variable(
            name=self.ast.name,
            dimensions=len(self.ast.indexes),
        )


class CallablePrototype(namedtuple("CallablePrototype", ["ast", "context", "description"])):
    __slots__ = []

    @property
    def name(self):
        return self.ast.declarator.name

    @property
    def parameter_declarations(self):
        return [
            ParameterDeclaration(ast=p, context=self.context)
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
            CallbackPrototype(callback, self.context, description=None)
            for callback in self.ast.callbacks
        ]

    @property
    def has_callbacks(self):
        return bool(self.callbacks)

    def validate(self):
        for callback in self.callbacks:
            yield from callback.validate()


class MethodPrototype(CallablePrototype):
    __slots__ = []


class CallbackPrototype(CallablePrototype):
    __slots__ = []

    def validate(self):
        for callback in self.callbacks:
            yield Diagnostic(
                Diagnostic.Messages.UNEXPECTED_CALLBACK,
                callback.name,
                parseinfo=callback.ast.parseinfo,
            )
        for parameter in self.parameter_declarations:
            if parameter.variable.dimensions:
                yield Diagnostic(
                    Diagnostic.Messages.CALLBACK_PARAMETERS_MUST_BE_SCALARS,
                    parseinfo=parameter.ast.parseinfo,
                )