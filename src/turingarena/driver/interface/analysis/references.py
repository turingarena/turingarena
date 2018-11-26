import logging
from collections import namedtuple

from turingarena.driver.interface.variables import ReferenceAction, ReferenceStatus, VariableAllocation
from turingarena.util.visitor import visitormethod


class ReferenceActionAnalyzer(namedtuple("ReferenceActionAnalyzer", ["context"])):

    def reference_actions(self, n):
        actions = tuple(self._get_actions(n))
        logging.debug(f"Actions: {n.__class__.__name__} {actions}")
        return actions

    def reference(self, e):
        r = self.context.reference(e)
        logging.debug(f"Reference: (bindings: {self.context.variable_mapping}) {e.__class__.__name__} -> {r}")
        return r

    def declared_reference(self, e):
        return self.context.declared_reference(e)

    @visitormethod
    def _get_actions(self, n):
        pass

    def _get_actions_Read(self, n):
        for a in n.arguments:
            yield ReferenceAction(self.declared_reference(a), ReferenceStatus.DECLARED)

    def _get_actions_Write(self, n):
        for a in n.arguments:
            yield ReferenceAction(self.reference(a), ReferenceStatus.RESOLVED)

    def _get_actions_ControlStructure(self, n):
        for b in n.bodies:
            yield from self.reference_actions(b)

    def _get_actions_SwitchValueResolve(self, n):
        yield ReferenceAction(self.reference(n.value), ReferenceStatus.RESOLVED)

    def _get_actions_CallbackStart(self, n):
        for p in n.callback_implementation.parameters:
            yield ReferenceAction(reference=p.as_reference(), status=ReferenceStatus.DECLARED)

    def _get_actions_Return(self, n):
        yield ReferenceAction(reference=self.reference(n.value), status=ReferenceStatus.RESOLVED)

    def _get_actions_For(self, n):
        for a in self.reference_actions(n.body):
            r = a.reference
            if r.index_count > 0:
                yield a._replace(reference=r._replace(index_count=r.index_count - 1))

    def _get_actions_CallArgumentsResolve(self, n):
        resolved_references = self.context.get_references(ReferenceStatus.RESOLVED)
        for p in n.arguments:
            reference = self.reference(p)
            if reference is not None and reference not in resolved_references:
                yield ReferenceAction(p.reference, ReferenceStatus.RESOLVED)

    def _get_actions_CallReturn(self, n):
        yield ReferenceAction(self.declared_reference(n.return_value), ReferenceStatus.DECLARED)

    def _get_actions_SequenceNode(self, n):
        for child in n.children:
            yield from self.reference_actions(child)

    def _get_actions_IntermediateNode(self, n):
        return ()

    def variable_allocations(self, n):
        return tuple(self._get_allocations(n))

    @visitormethod
    def _get_allocations(self, n):
        pass

    def _get_allocations_For(self, n):
        for a in self.reference_actions(n.body):
            if a.reference.variable.dimensions == 0:
                continue
            if a.status == ReferenceStatus.DECLARED:
                yield VariableAllocation(
                    variable=a.reference.variable,
                    indexes=n.context.index_variables[-a.reference.index_count + 1:],
                    size=n.index.range,
                )

    def _get_allocations_IntermediateNode(self, n):
        return ()
