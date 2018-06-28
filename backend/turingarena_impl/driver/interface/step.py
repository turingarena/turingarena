from abc import abstractmethod
from collections import namedtuple

from turingarena_impl.driver.interface.execution import Assignments
from turingarena_impl.driver.interface.nodes import IntermediateNode, Bindings, ExecutionResult
from turingarena_impl.driver.interface.variables import ReferenceStatus


class StepExecutor:
    @abstractmethod
    def execute(self, bindings: Bindings, step: 'Step') -> Assignments:
        pass


class Step(IntermediateNode, namedtuple("Step", ["children"])):
    __slots__ = []

    def _driver_run(self, context):
        assert self.children

        if context.phase is not None:
            return self._run_children(context)
        else:
            result = self._run_children(context._replace(
                phase=ReferenceStatus.RESOLVED,
                direction=self._get_direction(),
            ))
            context = context.extend(result)

            other_result = self._run_children(context._replace(
                phase=ReferenceStatus.DECLARED,
                direction=self._get_direction(),
            ))
            assert not other_result.assignments

            return result

    def _run_children(self, context):
        result = ExecutionResult([], None)
        for n in self.children:
            result = result.merge(n.driver_run(context.extend(result)))
        return result

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

    def _describe_node(self):
        if self._get_direction() is None:
            direction = "no direction"
        else:
            direction = self._get_direction().name.lower()
        yield f"step {direction} "
        for n in self.children:
            yield from self._indent_all(n.node_description)
