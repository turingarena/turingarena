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
        assert self.children

        if context.phase is not None:
            return self._run_children(context)
        else:
            assignments = self._run_children(context._replace(
                phase=ReferenceStatus.RESOLVED,
                direction=self._get_direction(),
            ))
            context = context.with_assigments(assignments)

            unexpected_assignments = self._run_children(context._replace(
                phase=ReferenceStatus.DECLARED,
                direction=self._get_direction(),
            ))
            assert not unexpected_assignments

            return assignments

    def _run_children(self, context):
        assignments = []
        for n in self.children:
            assignments.extend(
                n.driver_run(
                    context.with_assigments(assignments)
                )
            )
        return assignments

    def _get_declaration_directions(self):
        for n in self.children:
            yield from n.declaration_directions

    def _get_direction(self):
        if not self.declaration_directions:
            return None
        [direction] = self.declaration_directions
        return direction

    def _get_reference_actions(self):
        for n in self.children:
            yield from n.reference_actions
