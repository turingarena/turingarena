from abc import abstractmethod, ABCMeta
from collections import namedtuple

from turingarena_impl.interface.variables import Reference

AbstractSyntaxNodeWrapper = namedtuple("AbstractSyntaxNodeWrapper", ["ast", "context"])


class ImperativeStructure(metaclass=ABCMeta):
    __slots__ = []

    @abstractmethod
    def generate_instructions(self, bindings):
        pass

    @property
    def declared_references(self):
        references = list(self._get_declared_references())
        assert all(isinstance(r, Reference) for r in references)
        return references

    def _get_declared_references(self):
        return []

    @property
    def resolved_references(self):
        references = list(self._get_resolved_references())
        assert all(isinstance(r, Reference) for r in references)
        return references

    def _get_resolved_references(self):
        return []

    @abstractmethod
    def expects_request(self, request):
        pass

    @property
    def may_process_requests(self):
        return False


class Instruction:
    __slots__ = []

    def on_request_lookahead(self, request):
        pass

    def on_generate_response(self):
        pass

    def has_downward(self):
        return False

    def has_upward(self):
        return False

    def on_communicate_downward(self, lines):
        return NotImplemented

    def on_communicate_upward(self, lines):
        return NotImplemented

    def should_send_input(self):
        return False
