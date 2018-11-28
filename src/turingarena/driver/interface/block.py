import logging
from collections import namedtuple

from turingarena.driver.interface.seq import SequenceNode

logger = logging.getLogger(__name__)


class Block(namedtuple("Block", ["children"]), SequenceNode):
    __slots__ = []

    def _get_flat_children_builders(self):
        for ast in self.ast.statements:
            from turingarena.driver.interface.statements.statements import statement_classes
            for cls in statement_classes[ast.statement_type]:
                yield lambda context: context.compile(cls, ast)
