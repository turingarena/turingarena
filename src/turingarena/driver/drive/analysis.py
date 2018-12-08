from turingarena.driver.common.analysis import InterfaceAnalyzer
from turingarena.driver.common.nodes import *
from turingarena.driver.drive.nodes import *
from turingarena.driver.drive.requests import *
from turingarena.util.visitor import visitormethod

PHASES_MAP = {
    RequestLookahead: [
        ExecutionPhase.REQUEST,
    ],
    Read: [
        ExecutionPhase.DOWNWARD,
    ],
    Write: [
        ExecutionPhase.UPWARD,
    ],
    Checkpoint: [
        ExecutionPhase.UPWARD,
        ExecutionPhase.REQUEST,
    ],
    CallbackStart: [
        ExecutionPhase.UPWARD,
        ExecutionPhase.REQUEST,
    ],
    CallbackEnd: [
        ExecutionPhase.REQUEST,
    ],
    CallReturn: [
        ExecutionPhase.UPWARD,

        ExecutionPhase.REQUEST,
    ],
    Return: [
        ExecutionPhase.REQUEST,
    ],
}


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

    def can_be_grouped(self, n):
        return self._can_be_grouped(n)

    @visitormethod
    def _can_be_grouped(self, n):
        pass

    def _can_be_grouped_For(self, n):
        # no local references
        return all(
            isinstance(a.reference, Subscript)
            for a in self.reference_actions(n.body)
        ) and self.can_be_grouped(n.body)

    def _can_be_grouped_Block(self, n):
        return all(
            self.can_be_grouped(child)
            for child in n.children
        )

    def _can_be_grouped_Step(self, n):
        return self.can_be_grouped(n.body)

    def _can_be_grouped_object(self, n):
        for t in [
            Loop,
            AcceptCallbacks,
        ]:
            if isinstance(n, t):
                return False
        return True

    def phases(self, n):
        return frozenset(self._get_phases(n))

    @visitormethod
    def _get_phases(self, n):
        pass

    def _get_phases_Block(self, n):
        for child in n.children:
            yield from self.phases(child)

    def _get_phases_Step(self, n):
        yield from n.phases

    def _get_phases_For(self, n):
        yield from self.phases(n.body)

    def _get_phases_If(self, n):
        for body in n.branches:
            if body is not None:
                yield from self.phases(body)

    def _get_phases_Switch(self, n):
        for c in n.cases:
            yield from self.phases(c.body)

    def _get_phases_Loop(self, n):
        yield from self.phases(n.body)

    def _get_phases_AcceptCallbacks(self, n):
        for callback in n.callbacks:
            yield from self.phases(callback.body)

    def _get_phases_Callback(self, n):
        return self.phases(n.body)

    def _get_phases_object(self, n):
        for t, v in PHASES_MAP.items():
            if isinstance(n, t):
                yield from v
