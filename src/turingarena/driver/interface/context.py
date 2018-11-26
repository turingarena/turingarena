import logging
from collections import namedtuple
from typing import Optional

from turingarena.driver.interface.variables import ReferenceAction, ReferenceStatus, Variable, Reference
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
            ReferenceAction(reference=c.variable.as_reference(), status=ReferenceStatus.DECLARED)
            for c in self.constants
        ).with_reference_actions(
            ReferenceAction(reference=c.variable.as_reference(), status=ReferenceStatus.RESOLVED)
            for c in self.constants
        )

    @property
    def initial_context(self):
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

    @visitormethod
    def variable(self, e) -> Optional[Variable]:
        pass

    def variable_VariableReference(self, e):
        return self.variable_mapping.get(e.variable_name)

    def variable_Expression(self, e):
        return None

    @visitormethod
    def dimensions(self, e) -> int:
        pass

    def dimensions_Literal(self, e):
        return 0

    def dimensions_VariableReference(self, e):
        return self.variable(e).dimensions

    def dimensions_Subscript(self, e):
        array_dimensions = self.dimensions(e.array)
        if array_dimensions < 1:
            # not an array, fix
            return 0
        return array_dimensions - 1

    @visitormethod
    def reference(self, e) -> Optional[Reference]:
        pass

    def reference_VariableReference(self, e):
        variable = self.variable(e)
        if variable is not None:
            return variable.as_reference()

    def reference_Subscript(self, e):
        array_reference = self.reference(e.array)
        if array_reference is not None:
            return array_reference._replace(
                index_count=array_reference.index_count + 1,
            )

    def reference_Expression(self, e):
        return None

    def declared_reference(self, e, dimensions=0) -> Optional[Reference]:
        return self._declared_reference(e, dimensions)

    @visitormethod
    def _declared_reference(self, e, dimensions):
        pass

    def _declared_reference_VariableReference(self, e, dimensions):
        return Variable(name=e.variable_name, dimensions=dimensions).as_reference()

    def _declared_reference_Subscript(self, e, dimensions):
        array_reference = self.declared_reference(e.array, dimensions + 1)
        if array_reference is not None:
            return array_reference._replace(
                index_count=array_reference.index_count + 1,
            )

    def _declared_reference_Expression(self, e):
        return None

    @visitormethod
    def is_resolved(self, e) -> bool:
        pass

    def is_resolved_Literal(self, e):
        return True

    def is_resolved_VariableReference(self, e):
        return self.reference(e) in self.get_references(ReferenceStatus.RESOLVED)

    def is_resolved_Subscript(self, e):
        return (
                self.reference(e) in self.get_references(ReferenceStatus.RESOLVED)
                or self.is_resolved(e.array)
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
