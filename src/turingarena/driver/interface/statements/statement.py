from turingarena.driver.interface.common import AbstractSyntaxNodeWrapper
from turingarena.driver.interface.nodes import IntermediateNode


class AbstractStatement(IntermediateNode):
    __slots__ = []

    def _describe_node(self):
        if self.comment is not None:
            yield f"{self.__class__.__name__} {self.comment}"


class Statement(AbstractStatement, AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def statement_type(self):
        return self.ast.statement_type

    def _describe_node(self):
        yield str(self)
