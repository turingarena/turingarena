from abc import abstractmethod, ABCMeta
from collections import namedtuple
from typing import List, Optional

from turingarena_impl.interface.variables import ReferenceDirection, ReferenceAction

AbstractSyntaxNodeWrapper = namedtuple("AbstractSyntaxNodeWrapper", ["ast", "context"])


class ImperativeStructure(metaclass=ABCMeta):
    __slots__ = []

    @abstractmethod
    def expects_request(self, request):
        pass

    @property
    def may_process_requests(self):
        return False


class Instruction:
    __slots__ = []

    @property
    def reference_actions(self) -> List[ReferenceAction]:
        """
        List of references involved in this instruction.
        """
        actions = list(self._get_reference_actions())
        assert all(isinstance(a, ReferenceAction) for a in actions)
        return actions

    @property
    def direction(self) -> Optional[ReferenceDirection]:
        return self._get_direction()

    @abstractmethod
    def _get_reference_actions(self):
        pass

    @abstractmethod
    def _get_direction(self):
        pass

    def on_request_lookahead(self, bindings, request):
        pass

    def on_generate_response(self, bindings):
        pass

    def on_communicate_upward(self, bindings, lines):
        pass

    def on_communicate_downward(self, bindings, lines):
        pass


class Step(Instruction, namedtuple("Step", ["instructions"])):
    __slots__ = []

    def __init__(self, *args, **kwargs):
        super().__init__()
        assert self.instructions

        if self.direction is None:
            assert len(self.instructions) == 1
        else:
            assert all(inst.direction is self.direction for inst in self.instructions)

    def _get_direction(self):
        return self.instructions[0].direction

    def _get_reference_actions(self):
        for inst in self.instructions:
            yield from inst.reference_actions


class StatementInstruction(Instruction, namedtuple("StatementInstruction", ["statement"])):
    __slots__ = []
