import logging
from collections import namedtuple

from turingarena.common import ImmutableObject
from turingarena.interface.bindings import BindingStorage

logger = logging.getLogger(__name__)


class StaticGlobalContext(namedtuple("StaticGlobalContext", [
    "functions",
    "callbacks",
    "global_variables",
])):
    def with_variables(self, variables):
        global_variables = dict(self.global_variables)
        global_variables.update({
            v.name: v for v in variables
        })
        return self._replace(global_variables=global_variables)

    def with_function(self, f):
        functions = dict(self.functions)
        functions[f.name] = f
        return self._replace(functions=functions)

    def with_callback(self, c):
        callbacks = dict(self.callbacks)
        callbacks[c.name] = c
        return self._replace(callbacks=callbacks)

    def create_local(self):
        return StaticLocalContext(
            global_context=self,
            outer_context=None,
            local_variables={},
        )


class StaticLocalContext(namedtuple("StaticLocalContext", [
    "global_context",
    "outer_context",
    "local_variables",
])):
    def with_variables(self, variables):
        local_variables = dict(self.local_variables)
        local_variables.update({
            v.name: v for v in variables
        })
        return self._replace(local_variables=local_variables)

    @property
    def variables(self):
        # FIXME: useless copies, use an immutable collection instead
        if self.outer_context:
            ans = dict(self.outer_context.variables)
        else:
            ans = dict(self.global_context.global_variables)
        ans.update(self.local_variables)
        return ans

    def create_inner(self):
        return StaticLocalContext(
            global_context=self.global_context,
            outer_context=self,
            local_variables={},
        )


class GlobalContext(ImmutableObject):
    __slots__ = ["interface", "variables", "bindings"]

    def __init__(self, interface):
        super().__init__(
            interface=interface,
            variables=interface.global_variables,
            bindings=BindingStorage(local_variables=interface.global_variables, parent=None),
        )


class ProcedureContext:
    def child(self, local_variables):
        return LocalContext(
            procedure=self,
            outer=self.global_context,
            local_variables=local_variables,
        )


class MainContext(ProcedureContext, namedtuple("MainContext", ["global_context"])):
    __slots__ = []


class CallbackContext(ProcedureContext, namedtuple("CallbackContext", [
    "global_context",
    "accept_context",
])):
    __slots__ = []


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
