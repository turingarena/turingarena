from collections import namedtuple

from turingarena.driver.interface.phase import ExecutionPhase
from turingarena.driver.interface.seq import SequenceNode
from turingarena.driver.interface.variables import ReferenceDirection


class Step(SequenceNode, namedtuple("Step", ["children"])):
    __slots__ = []

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
