from collections import namedtuple

from turingarena.driver.interface.analysis.direction import DeclarationDirectionAnalyzer
from turingarena.driver.interface.analysis.first import FirstRequestAnalyzer
from turingarena.driver.interface.statements.call import MethodCallbacksNode
from turingarena.driver.interface.statements.loop import Loop
from turingarena.util.visitor import visitormethod


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
