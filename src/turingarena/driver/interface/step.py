from collections import namedtuple

from turingarena.driver.interface.phase import ExecutionPhase
from turingarena.driver.interface.seq import SequenceNode
from turingarena.driver.interface.variables import ReferenceDirection


class Step(SequenceNode, namedtuple("Step", ["children"])):
    __slots__ = []

    def _driver_run(self, context):
        assert self.children

        if context.phase is not None:
            return self._run_children(context)
        else:
            result = context.result()
            for phase in ExecutionPhase:
                if phase == ExecutionPhase.UPWARD and self.direction != ReferenceDirection.UPWARD:
                    continue
                result = result.merge(self._run_children(context.extend(result)._replace(
                    phase=phase,
                )))

            return result

    def _run_children(self, context):
        result = context.result()
        for n in self.children:
            result = result.merge(n.driver_run(context.extend(result)))
        return result

    @property
    def direction(self):
        if not self.declaration_directions:
            return None
        [direction] = self.declaration_directions
        return direction

    def _describe_node(self):
        if self.direction is None:
            direction = "no direction"
        else:
            direction = self.direction.name.lower()
        yield f"step {direction} "
        for n in self.children:
            yield from self._indent_all(n.node_description)
