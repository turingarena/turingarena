from turingarena.driver.interface.common import AbstractSyntaxNodeWrapper


class Statement(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def statement_type(self):
        return self.ast.statement_type

    def _describe_node(self):
        yield str(self)
