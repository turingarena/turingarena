import logging
from collections import namedtuple

from turingarena.driver.interface.requests import RequestSignature, CallRequestSignature
from turingarena.util.visitor import visitormethod


class StatementAnalyzer(namedtuple("StatementAnalyzer", [])):
    def first_requests(self, n):
        logging.debug(f"first_requests({n.__class__.__name__}) -> {frozenset(self._get_first_requests(n))}")
        return frozenset(self._get_first_requests(n))

    @visitormethod
    def _get_first_requests(self, n):
        pass

    def _get_first_requests_Exit(self, n):
        yield RequestSignature("exit")

    def _get_first_requests_Call(self, n):
        yield CallRequestSignature("call", n.method_name)

    def _get_first_requests_SequenceNode(self, n):
        for child in n.children:
            logging.debug(f"first_requests_SequenceNode({n.__class__.__name__}) visiting {child.__class__.__name__}")
            for r in self.first_requests(child):
                if r is not None:
                    yield r
            if None not in self.first_requests(child):
                break
        else:
            yield None

    def _get_first_requests_For(self, n):
        yield None
        yield from self.first_requests(n.body)

    def _get_first_requests_Loop(self, n):
        yield None
        yield from self.first_requests(n.body)

    def _get_first_requests_Switch(self, n):
        for c in n.cases:
            yield from self.first_requests(c.body)

    def _get_first_requests_If(self, n):
        yield from self.first_requests(n.then_body)
        if n.else_body is not None:
            yield from self.first_requests(n.else_body)
        else:
            yield None

    def _get_first_requests_IntermediateNode(self, n):
        yield None


class ContextStatementAnalyzer(namedtuple("ContextStatementAnalyzer", ["context"])):
    pass