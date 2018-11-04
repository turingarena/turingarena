import logging
from collections import namedtuple

from turingarena_impl.driver.interface.variables import ReferenceAction, ReferenceStatus

logger = logging.getLogger(__name__)


class InterfaceContext(namedtuple("InterfaceContext", [
    "methods",
    "constants",
])):
    @property
    def methods_by_name(self):
        return {m.name: m for m in self.methods}

    def main_block_context(self):
        return StatementContext(
            global_context=self,
            reference_actions=(),
            index_variables=(),
            main_block=True,
            in_loop=False,
        )


class StatementContext(namedtuple("StatementContext", [
    "global_context",
    "reference_actions",
    "index_variables",
    "main_block",
    "in_loop",
])):
    def with_reference_actions(self, actions):
        actions = tuple(actions)
        assert all(
            isinstance(a, ReferenceAction) and
            a.reference is not None
            for a in actions
        )
        return self._replace(
            reference_actions=self.reference_actions + actions
        )

    def get_references(self, status):
        return {
            a.reference
            for a in self.reference_actions
            if a.status is status
        }

    @property
    def declared_variables(self):
        return {
            r.variable
            for r in self.get_references(ReferenceStatus.DECLARED)
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

    def expression(self, **kwargs):
        options = dict(
            index_count=0,
            declaring=False,
            reference=False,
            resolved=False,
        )
        options.update(kwargs)
        return ExpressionContext(
            statement_context=self,
            **options,
        )


class ExpressionContext(namedtuple("ExpressionContext", [
    "statement_context",
    "declaring",
    "reference",
    "resolved",
    "index_count",
])):
    # TODO: wrap all options into an optional field of type ReferenceContext
    pass


class StaticCallbackBlockContext(namedtuple("StaticCallbackBlockContext", [
    "local_context",
    "callback_index",
])):
    pass
