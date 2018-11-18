from turingarena.driver.interface.statements.call import MethodReturnNode
from turingarena.driver.interface.statements.callback import CallbackCallNode
from turingarena.driver.interface.statements.io import Read, Checkpoint
from turingarena.driver.interface.variables import ReferenceDirection
from turingarena.util.visitor import visitormethod


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

    def _get_directions_ControlStructure(self, n):
        for b in n.bodies:
            yield from self.declaration_directions(b)

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
