import logging
from collections import namedtuple

from turingarena_impl.interface.variables import ReferenceAction, ReferenceActionType

logger = logging.getLogger(__name__)


class InterfaceContext(namedtuple("InterfaceContext", [
    "methods",
])):
    @property
    def methods_by_name(self):
        return {m.name: m for m in self.methods}

    def main_block_context(self):
        return StatementContext(
            global_context=self,
            reference_actions=(),
            index_variables=(),
            in_loop=False,
        )


class StatementContext(namedtuple("StatementContext", [
    "global_context",
    "reference_actions",
    "index_variables",
    "in_loop",
])):
    def with_reference_actions(self, actions):
        actions = tuple(actions)
        assert all(isinstance(r, ReferenceAction) for r in actions)
        return self._replace(
            reference_actions=self.reference_actions + actions
        )

    def get_references(self, action_type):
        return {
            a.reference
            for a in self.reference_actions
            if a.action_type is action_type
        }

    @property
    def declared_variables(self):
        return {
            r.variable
            for r in self.get_references(ReferenceActionType.DECLARED)
        }

    @property
    def variable_mapping(self):
        return {v.name: v for v in self.declared_variables}

    def with_index_variable(self, variable):
        return self._replace(
            index_variables=self.index_variables + (variable,),
        )

    def with_loop(self):
        return self._replace(in_loop=True)


class StaticCallbackBlockContext(namedtuple("StaticCallbackBlockContext", [
    "local_context",
    "callback_index",
])):
    pass
