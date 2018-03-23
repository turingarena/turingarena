import logging
from collections import namedtuple

from turingarena.common import ImmutableObject

logger = logging.getLogger(__name__)

StaticContext = namedtuple("StaticContext", [
    "declared_callbacks",
    "global_variables",
    "variables",
    "functions",
])


class BindingStorage:
    def __init__(self, *, local_variables, parent):
        self.local_variables = local_variables
        self.parent = parent
        self.values = {
            l: None for l in self.local_variables.values()
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
    __slots__ = ["interface", "variables", "bindings"]

    def __init__(self, interface):
        super().__init__(
            interface=interface,
            variables=interface.global_variables,
            bindings=BindingStorage(local_variables=interface.global_variables, parent=None),
        )


class ProcedureContext(ImmutableObject):
    __slots__ = ["global_context"]

    def child(self, local_variables):
        return LocalContext(
            procedure=self,
            outer=self.global_context,
            local_variables=local_variables,
        )


class MainContext(ProcedureContext):
    __slots__ = []


class CallbackContext(ProcedureContext):
    __slots__ = ["accept_context", "parameters"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs, parameters=None)


class LocalContext:
    __slots__ = [
        "procedure",
        "outer",
        "local_variables",
        "bindings",
    ]

    def __init__(self, *, procedure, outer, local_variables):
        if outer is None:
            parent = procedure.global_context.bindings
        else:
            parent = outer.bindings
        self.local_variables = local_variables
        self.bindings = BindingStorage(local_variables=local_variables, parent=parent)
        self.procedure = procedure
        self.outer = outer

    @property
    def variables(self):
        return dict(self.outer.variables, **self.local_variables)

    def child(self, local_variables):
        return LocalContext(
            procedure=self.procedure,
            outer=self,
            local_variables=local_variables,
        )


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
