from turingarena.interface.node import AbstractSyntaxNodeWrapper
from turingarena.interface.statements import get_statement_classes


class Statement(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def statement_type(self):
        return get_statement_classes().inv[self.__class__]

    @property
    def context_after(self):
        return self.context

    def validate(self):
        yield
