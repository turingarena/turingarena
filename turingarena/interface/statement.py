from turingarena.interface.node import AbstractSyntaxNode
from turingarena.interface.statements import get_statement_classes


class Statement(AbstractSyntaxNode):
    __slots__ = ["ast"]

    @property
    def statement_type(self):
        return get_statement_classes().inv[self.__class__]

    def update_context(self, context):
        return context

    def validate(self, context):
        pass
