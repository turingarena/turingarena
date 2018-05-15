from abc import abstractmethod
from collections import namedtuple


AbstractSyntaxNodeWrapper = namedtuple("AbstractSyntaxNodeWrapper", ["ast", "context"])


class ImperativeStructure(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @abstractmethod
    def generate_instructions(self, context):
        pass

    @abstractmethod
    def expects_request(self, request):
        pass

    @property
    def may_process_requests(self):
        return False

    @property
    @abstractmethod
    def context_after(self):
        pass


class Instruction:
    __slots__ = []

    def on_request_lookahead(self, request):
        pass

    def on_generate_response(self):
        pass

    def on_communicate_with_process(self, connection):
        pass

    def should_send_input(self):
        return False
