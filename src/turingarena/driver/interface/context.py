import logging
from collections import namedtuple
from functools import partial

from turingarena.driver.interface.analysis import TreeAnalyzer
from turingarena.driver.interface.validate import Validator
from turingarena.driver.interface.variables import ReferenceAllocation, ReferenceDeclaration, \
    ReferenceResolution
from turingarena.util.visitor import visitormethod

logger = logging.getLogger(__name__)


class InterfaceContext(namedtuple("InterfaceContext", [
    "methods",
    "constants",
])):
    @property
    def methods_by_name(self):
        return {m.name: m for m in self.methods}

    @property
    def main_block_context(self):
        return self.initial_context.with_reference_actions(
            a(c.variable.as_reference())
            for c in self.constants
            for a in [
                partial(ReferenceDeclaration, dimensions=0),
                ReferenceResolution,
            ]
        )

    @property
    def initial_context(self):
        return INITIAL_CONTEXT._replace(global_context=self)


class StatementContext(namedtuple("StatementContext", [
    "global_context",
    "prev_reference_actions",
    "index_variables",
    "main_block",
    "in_loop",
]), Validator, TreeAnalyzer):
    def with_reference_actions(self, actions):
        actions = tuple(actions)
        assert all(
            a.reference is not None
            for a in actions
        )
        return self._replace(
            prev_reference_actions=self.prev_reference_actions + actions
        )

    def get_resolved_references(self):
        return {
            a.reference
            for a in self.prev_reference_actions
            if isinstance(a, ReferenceResolution)
        }

    @property
    def reference_declaration_mapping(self):
        return {
            a.reference.variable.name: a
            for a in self.prev_reference_actions
            if isinstance(a, ReferenceDeclaration)
        }

    def with_index_variable(self, variable):
        return self._replace(
            index_variables=self.index_variables + (variable,),
        )

    def with_loop(self):
        return self._replace(in_loop=True)

    def is_relevant(self, n):
        "Whether this node should be kept in the parent block"
        return self._is_relevant(n)

    @visitormethod
    def _is_relevant(self, n):
        pass

    def _is_relevant_SwitchValueResolve(self, n):
        return not self.is_resolved(n.value)

    def _is_relevant_IfConditionResolve(self, n):
        return not self.is_resolved(n.condition)

    def _is_relevant_CallReturn(self, n):
        return n.return_value is not None

    def _is_relevant_PrintNoCallbacks(self, n):
        return n.method and n.method.callbacks

    def _is_relevant_AcceptCallbacks(self, n):
        return n.method and n.method.has_callbacks

    def _is_relevant_IntermediateNode(self, n):
        return True

    @visitormethod
    def dimensions(self, e) -> int:
        pass

    def dimensions_Literal(self, e):
        return 0

    def dimensions_VariableReference(self, e):
        try:
            reference_declaration = self.reference_declaration_mapping[e.variable_name]
        except KeyError:
            return 0
        return reference_declaration.dimensions

    def dimensions_Subscript(self, e):
        array_dimensions = self.dimensions(e.array)
        if array_dimensions < 1:
            # not an array, fix
            return 0
        return array_dimensions - 1

    @visitormethod
    def is_resolved(self, e) -> bool:
        pass

    def is_resolved_Reference(self, r):
        return r in self.get_resolved_references()

    def is_resolved_Literal(self, e):
        return True

    def is_resolved_VariableReference(self, e):
        return self.is_resolved(self.reference(e))

    def is_resolved_Subscript(self, e):
        return (
                self.is_resolved(self.reference(e))
                or self.is_resolved(e.array)
        )


INITIAL_CONTEXT = StatementContext(
    global_context=None,
    prev_reference_actions=(),
    index_variables=(),
    main_block=True,
    in_loop=False,
)
