from turingarena.driver.interface.common import AbstractSyntaxNodeWrapper
from turingarena.driver.interface.nodes import IntermediateNode


class AbstractStatement(IntermediateNode):
    __slots__ = []

    def _describe_node(self):
        if self.comment is not None:
            yield f"{self.statement_type} {self.comment}"


class Statement(AbstractStatement, AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def statement_type(self):
        return self.ast.statement_type

    def __str__(self):
        from turingarena.driver.generator import StatementDescriptionCodeGen
        return "".join(StatementDescriptionCodeGen().statement(self))

    def _describe_node(self):
        yield str(self)


class SyntheticStatement(AbstractStatement):
    __slots__ = ["statement_type", "_comment", "__dict__"]

    def __init__(self, statement_type, comment, **kwargs):
        self.statement_type = statement_type
        self._comment = comment
        self.__dict__ = kwargs

    def _get_intermediate_nodes(self):
        return []

    def _get_comment(self):
        return f"({self._comment})"
