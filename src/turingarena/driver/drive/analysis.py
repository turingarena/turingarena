from enum import Enum

from turingarena.driver.common.analysis import InterfaceAnalyzer
from turingarena.driver.common.nodes import *
from turingarena.driver.drive.nodes import *
from turingarena.driver.drive.requests import *
from turingarena.util.visitor import visitormethod

ReferenceDirection = Enum("ReferenceDirection", names=["DOWNWARD", "UPWARD"])

DIRECTION_MAP = {
    ReferenceDirection.DOWNWARD: [
        Read,
    ],
    ReferenceDirection.UPWARD: [
        CallbackStart,
        CallReturn,
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
            Checkpoint,
        ]:
            if isinstance(n, t):
                return False
        return True

    def declaration_directions(self, n):
        return frozenset(self._get_directions(n))

    @visitormethod
    def _get_directions(self, n):
        pass

    def _get_directions_Block(self, n):
        for child in n.children:
            yield from self.declaration_directions(child)

    def _get_directions_Step(self, n):
        if n.direction is not None:
            yield n.direction

    def _get_directions_For(self, n):
        yield from self.declaration_directions(n.body)

    def _get_directions_If(self, n):
        for body in n.branches:
            if body is not None:
                yield from self.declaration_directions(body)

    def _get_directions_Switch(self, n):
        for c in n.cases:
            yield from self.declaration_directions(c.body)

    def _get_directions_Loop(self, n):
        yield from self.declaration_directions(n.body)

    def _get_directions_AcceptCallbacks(self, n):
        for callback in n.callbacks:
            yield from self.declaration_directions(callback.body)

    def _get_directions_Callback(self, n):
        return self.declaration_directions(n.body)

    def _get_directions_object(self, n):
        for d, ts in DIRECTION_MAP.items():
            for t in ts:
                if isinstance(n, t):
                    yield d
