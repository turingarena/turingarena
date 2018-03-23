import logging
from collections import namedtuple

from turingarena.common import ImmutableObject

logger = logging.getLogger(__name__)

StaticContext = namedtuple("StaticContext", [
    "scope",
    "global_variables",
])


class BindingStorage:
    def __init__(self, *, scope, parent):
        self.scope = scope
        self.parent = parent
        self.values = {
            l: None for l in self.scope.variables.locals().values()
        }

    def __getitem__(self, variable):
        if variable in self.values:
            return self.values[variable]
        elif self.parent:
            return self.parent[variable]
        else:
            raise KeyError(variable)

    def __setitem__(self, variable, value):
        if variable in self.values:
            self.values[variable] = value
        elif self.parent:
            self.parent[variable] = value
        else:
            raise KeyError(variable)


class GlobalContext(ImmutableObject):
    __slots__ = ["interface", "bindings"]

    def __init__(self, interface):
        super().__init__(
            interface=interface,
            bindings=BindingStorage(scope=interface.body.scope, parent=None),
        )


class ProcedureContext(ImmutableObject):
    __slots__ = ["global_context"]

    def child(self, scope):
        return LocalContext(procedure=self, outer=None, scope=scope)


class MainContext(ProcedureContext):
    __slots__ = []


class CallbackContext(ProcedureContext):
    __slots__ = ["accept_context", "parameters"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs, parameters=None)


class LocalContext:
    __slots__ = ["procedure", "scope", "outer", "bindings"]

    def __init__(self, *, procedure, outer, scope):
        if outer is None:
            parent = procedure.global_context.bindings
        else:
            parent = outer.bindings
        self.scope = scope
        self.bindings = BindingStorage(scope=scope, parent=parent)
        self.procedure = procedure
        self.outer = outer

    def child(self, scope):
        return LocalContext(procedure=self.procedure, outer=self, scope=scope)


class FunctionCallContext:
    __slots__ = ["local_context", "accepted_callbacks"]

    def __init__(self, local_context):
        self.local_context = local_context
        self.accepted_callbacks = None


class AcceptCallbackContext:
    __slots__ = ["call_context", "callback"]

    def __init__(self, call_context):
        self.call_context = call_context
        self.callback = None
