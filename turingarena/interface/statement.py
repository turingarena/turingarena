from turingarena.interface.node import AbstractSyntaxNode
from turingarena.interface.statements import get_statement_classes


class Statement(AbstractSyntaxNode):
    __slots__ = ["ast", "context"]

    @property
    def statement_type(self):
        return get_statement_classes().inv[self.__class__]

    @property
    def context_after(self):
        return self.context

    def validate(self):
        pass
