from collections.__init__ import namedtuple

from turingarena.driver.interface.analysis import TreeAnalyzer
from turingarena.driver.interface.nodes import Print, IntLiteral, Comment, Flush, PrintNoCallbacks
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

    def transform_Callback(self, n):
        n = super().transform_Callback(n)
        return n._replace(
            body=n.body._replace(
                children=tuple([
                    Print([IntLiteral(1), IntLiteral(n.index)]),
                    *n.body.children,
                ]),
            ),
        )

    def transform_Block(self, n):
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

        yield from self.transform_all(self.replacement_nodes(n))

    @visitormethod
    def replacement_nodes(self, n):
        pass

    def replacement_nodes_object(self, n):
        yield n

    def replacement_nodes_Read(self, n):
        yield Flush()
        yield n

    def replacement_nodes_Call(self, n):
        yield n
        if n.method.callbacks:
            yield PrintNoCallbacks()
