from collections.__init__ import namedtuple

from turingarena.driver.interface.analysis import TreeAnalyzer
from turingarena.driver.interface.nodes import Print, IntLiteral, Comment, Flush
from turingarena.driver.interface.transform import TreeTransformer
from turingarena.util.visitor import visitormethod


class TreePreprocessor(namedtuple("TreeTransformer", [
    "flushed",
]), TreeAnalyzer, TreeTransformer):
    @classmethod
    def create(cls):
        return cls(
            flushed=False,
        )

    def transform_Write(self, s):
        return Print(s.arguments)

    def transform_Checkpoint(self, s):
        return Print([IntLiteral(0)])

    def transform_PrintNoCallbacks(self, s):
        return Print([IntLiteral(0), IntLiteral(0)])

    def transform_PrintCallbackRequest(self, s):
        return Print([IntLiteral(1), IntLiteral(s.index)])

    def transform_SequenceNode(self, n):
        children = []
        for c in n.children:
            children.extend(self.statement_nodes(c))
        return n._replace(
            children=tuple(children),
        )

    def statement_nodes(self, n):
        comment = self.comment(n)
        if comment is not None:
            yield Comment(comment)

        yield from self.variable_declarations(n)
        yield from self.reference_allocations(n)

        yield from self.extra_nodes(n)
        yield self.transform(n)

    @visitormethod
    def extra_nodes(self, n):
        pass

    def extra_nodes_object(self, n):
        return []

    def extra_nodes_Read(self, n):
        yield Flush()
