from abc import abstractmethod, ABCMeta
from collections import namedtuple

from turingarena_impl.interface.variables import ReferenceAction

AbstractSyntaxNodeWrapper = namedtuple("AbstractSyntaxNodeWrapper", ["ast", "context"])


class ImperativeStructure(metaclass=ABCMeta):
    __slots__ = []

    @abstractmethod
    def generate_instructions(self, bindings):
        pass

    @property
    def instructions(self):
        return list(self._get_instructions())

    @abstractmethod
    def _get_instructions(self):
        pass

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


class StatementInstruction(Instruction, namedtuple("StatementInstruction", ["statement"])):
    pass
