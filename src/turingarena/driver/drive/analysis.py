from turingarena.driver.common.analysis import InterfaceAnalyzer
from turingarena.driver.drive.requests import RequestSignature, CallRequestSignature
from turingarena.util.visitor import visitormethod


class ExecutionAnalyzer(InterfaceAnalyzer):
    def first_requests(self, n):
        return frozenset(self._get_first_requests(n))

    @visitormethod
    def _get_first_requests(self, n):
        pass

    def _get_first_requests_Exit(self, n):
        yield RequestSignature("exit")

    def _get_first_requests_Call(self, n):
        yield CallRequestSignature("call", n.method.name)

    def _get_first_requests_Block(self, n):
        for child in n.children:
            for r in self.first_requests(child):
                if r is not None:
                    yield r
            if None not in self.first_requests(child):
                break
        else:
            yield None

    def _get_first_requests_Step(self, n):
        return self.first_requests(n.body)

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
        for body in n.branches:
            if body is None:
                yield None
            else:
                yield from self.first_requests(body)

    def _get_first_requests_object(self, n):
        yield None
