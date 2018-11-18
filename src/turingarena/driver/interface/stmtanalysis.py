import logging
from collections import namedtuple

from turingarena.driver.interface.requests import RequestSignature, CallRequestSignature
from turingarena.driver.interface.statements.call import MethodReturnNode, MethodCallbacksNode
from turingarena.driver.interface.statements.callback import CallbackCallNode
from turingarena.driver.interface.statements.io import Read, Checkpoint
from turingarena.driver.interface.statements.loop import Loop
from turingarena.driver.interface.variables import ReferenceDirection
from turingarena.util.visitor import visitormethod


class FirstRequestAnalyzer:
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


class DeclarationDirectionAnalyzer:
    def declaration_directions(self, n):
        return frozenset(self._get_directions(n))

    DIRECTION_MAP = {
        ReferenceDirection.DOWNWARD: [
            Read,
        ],
        ReferenceDirection.UPWARD: [
            Checkpoint,
            CallbackCallNode,
            MethodReturnNode,
        ],
    }

    @visitormethod
    def _get_directions(self, n):
        pass

    def _get_directions_SequenceNode(self, n):
        for child in n.children:
            yield from self.declaration_directions(child)

    def _get_directions_For(self, n):
        return self.declaration_directions(n.body)

    def _get_directions_Loop(self, n):
        return self.declaration_directions(n.body)

    def _get_directions_If(self, n):
        for b in n.branches:
            yield from self.declaration_directions(b)

    def _get_directions_Switch(self, n):
        for c in n.cases:
            yield from self.declaration_directions(c.body)

    def _get_directions_MethodCallbacksNode(self, n):
        for callback in n.callbacks:
            yield from self.declaration_directions(callback.body)

    def _get_directions_CallbackImplementation(self, n):
        return self.declaration_directions(n.body)

    def _get_directions_IntermediateNode(self, n):
        for d, ts in self.DIRECTION_MAP.items():
            for t in ts:
                if isinstance(n, t):
                    yield d


class StatementAnalyzer(
    namedtuple("StatementAnalyzer", []),
    FirstRequestAnalyzer,
    DeclarationDirectionAnalyzer,
):
    @visitormethod
    def can_be_grouped(self, n):
        pass

    def can_be_grouped_For(self, n):
        # no local references
        return all(
            a.reference.index_count > 0
            for a in n.body.reference_actions
        ) and all(
            self.can_be_grouped(child)
            for child in n.body.children
        )

    NON_GROUPABLE = [
        Loop,
        MethodCallbacksNode,
    ]

    def can_be_grouped_IntermediateNode(self, n):
        for t in self.NON_GROUPABLE:
            if isinstance(n, t):
                return False
        return True

    def step_direction(self, n):
        directions = self.declaration_directions(n)
        if not directions:
            return None
        [direction] = directions
        return direction
