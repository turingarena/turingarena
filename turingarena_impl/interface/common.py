from abc import abstractmethod, ABCMeta
from collections import namedtuple

from turingarena_impl.interface.variables import ReferenceAction

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
    def reference_actions(self):
        references = list(self._get_reference_actions())
        assert all(isinstance(r, ReferenceAction) for r in references)
        return references

    def _get_reference_actions(self):
        return []

    @property
    def has_downward(self):
        return False

    @property
    def has_upward(self):
        return False

    def generate_child_instructions(self, bindings):
        pass

    def on_request_lookahead(self, bindings, request):
        pass

    def on_generate_response(self, bindings):
        pass

    def on_communicate_upward(self, bindings, lines):
        pass

    def on_communicate_downward(self, bindings, lines):
        pass


class Step(namedtuple("Step", ["instructions"])):
    __slots__ = []


class StatementInstruction(Instruction, namedtuple("StatementInstruction", ["statement"])):
    __slots__ = []
