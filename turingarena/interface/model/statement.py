from turingarena.interface.model.node import AbstractSyntaxNode
from turingarena.interface.model.statements import get_statement_classes


class Statement(AbstractSyntaxNode):
    __slots__ = ["statement_type"]

    def __init__(self, **kwargs):
        super().__init__(statement_type=get_statement_classes().inv[self.__class__], **kwargs)


class ImperativeStatement(Statement):
    __slots__ = []

    def run(self, context):
        yield from []

    def first_calls(self):
        return {None}
