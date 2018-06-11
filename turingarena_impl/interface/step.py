from abc import abstractmethod
from collections import namedtuple

from turingarena_impl.interface.engine import NodeExecutionContext, Assignments
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
        assignments = self._run_node_sequence(self.children, context._replace(
            phase=ReferenceStatus.RESOLVED,
        ))
        self._run_node_sequence(self.children, context.with_assigments(assignments)._replace(
            phase=ReferenceStatus.DECLARED,
        ))
        return assignments

    def _get_direction(self):
        return self.children[0].direction

    def _get_reference_actions(self):
        for n in self.children:
            yield from n.reference_actions
