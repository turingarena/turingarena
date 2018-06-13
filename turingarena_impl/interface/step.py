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

    def __init__(self, *args, **kwargs):
        super().__init__()
        assert self.children

        if self.direction is None:
            assert len(self.children) == 1
        else:
            assert all(n.direction is self.direction for n in self.children)

    def _driver_run(self, context: NodeExecutionContext):
        assert context.phase is None
        assignments = []
        for n in self.children:
            inner_assigments = n.driver_run(context._replace(
                phase=ReferenceStatus.RESOLVED,
                direction=self.direction,
            ))
            assignments.extend(inner_assigments)
            context = context.with_assigments(inner_assigments)

        for n in self.children:
            n.driver_run(context._replace(
                phase=ReferenceStatus.DECLARED,
                direction=self.direction,
            ))
        return assignments

    def _get_direction(self):
        return self.children[0].direction

    def _get_reference_actions(self):
        for n in self.children:
            yield from n.reference_actions
