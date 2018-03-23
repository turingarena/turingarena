from turingarena.interface.node import AbstractSyntaxNode
from turingarena.interface.statements import get_statement_classes


class Statement(AbstractSyntaxNode):
    __slots__ = ["ast"]

    @property
    def statement_type(self):
        return get_statement_classes().inv[self.__class__]

    def validate(self, context):
        pass
