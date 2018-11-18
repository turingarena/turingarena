from collections import namedtuple

from turingarena.driver.interface.seq import SequenceNode


class Step(SequenceNode, namedtuple("Step", ["children"])):
    __slots__ = []

    def _describe_node(self):
        from turingarena.driver.interface.stmtanalysis import StatementAnalyzer
        direction = StatementAnalyzer().step_direction(self)
        if direction is None:
            direction = "no direction"
        else:
            direction = direction.name.lower()
        yield f"step {direction} "
        for n in self.children:
            yield from self._indent_all(n.node_description)
