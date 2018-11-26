from collections import namedtuple

from turingarena.driver.interface.seq import SequenceNode


class Step(SequenceNode, namedtuple("Step", ["children", "direction"])):
    __slots__ = []

    def _describe_node(self):
        if self.direction is None:
            direction = "no direction"
        else:
            direction = self.direction.name.lower()
        yield f"step {direction} "
        for n in self.children:
            yield from self._indent_all(n.node_description)
