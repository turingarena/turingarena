from turingarena.driver.interface.common import ImperativeStructure, AbstractSyntaxNodeWrapper
from turingarena.driver.interface.nodes import IntermediateNode


class AbstractStatement(ImperativeStructure, IntermediateNode):
    __slots__ = []


class Statement(AbstractStatement, AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def statement_type(self):
        return self.ast.statement_type

    def __str__(self):
        from turingarena.driver.generator import StatementDescriptionCodeGen
        return "".join(StatementDescriptionCodeGen().statement(self))


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
