from abc import abstractmethod
from collections import namedtuple

from turingarena_impl.interface.execution import NodeExecutionContext, Assignments
from turingarena_impl.interface.nodes import IntermediateNode, Bindings
from turingarena_impl.interface.variables import ReferenceStatus


class StepExecutor:
    @abstractmethod
    def execute(self, bindings: Bindings, step: 'Step') -> Assignments:
        pass


class Step(IntermediateNode, namedtuple("Step", ["children"])):
    __slots__ = []

    def _driver_run(self, context: NodeExecutionContext):
        assert context.phase is None
        assert self.children

        assignments = []
        for n in self.children:
            inner_assigments = n.driver_run(context._replace(
                phase=ReferenceStatus.RESOLVED,
            ))
            assignments.extend(inner_assigments)
            context = context.with_assigments(inner_assigments)

        for n in self.children:
            n.driver_run(context._replace(
                phase=ReferenceStatus.DECLARED,
            ))
        return assignments

    def _get_declaration_directions(self):
        for n in self.children:
            yield from n.declaration_directions

    def _get_reference_actions(self):
        for n in self.children:
            yield from n.reference_actions
