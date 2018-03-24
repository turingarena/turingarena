from turingarena.interface.node import AbstractSyntaxNode
from turingarena.interface.statements import get_statement_classes


class Statement(AbstractSyntaxNode):
    __slots__ = ["ast", "context"]

    @property
    def statement_type(self):
        return get_statement_classes().inv[self.__class__]

    @property
    def context_after(self):
        # TODO: remove delegation
        return self.update_context(self.context)

    def update_context(self, context):
        return context

    def validate(self, context):
        pass
