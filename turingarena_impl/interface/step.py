from collections import namedtuple

from turingarena_impl.interface.nodes import IntermediateNode


class Step(IntermediateNode, namedtuple("Step", ["children"])):
    __slots__ = []

    def __init__(self, *args, **kwargs):
        super().__init__()
        assert self.children

        if self.direction is None:
            assert len(self.children) == 1
        else:
            assert all(n.direction is self.direction for n in self.children)

    def _get_direction(self):
        return self.children[0].direction

    def _get_reference_actions(self):
        for n in self.children:
            yield from n.reference_actions
