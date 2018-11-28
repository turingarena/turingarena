import logging
from abc import abstractmethod
from functools import partial

from turingarena.driver.interface.common import AbstractSyntaxNodeWrapper, memoize
from turingarena.driver.interface.seq import SequenceNode
from turingarena.driver.interface.step import Step

logger = logging.getLogger(__name__)


class AbstractBlock(SequenceNode):
    @property
    @memoize
    def flat_inner_nodes(self):
        return tuple(self._generate_flat_inner_nodes())

    @abstractmethod
    def _generate_flat_inner_nodes(self):
        pass

    @property
    @memoize
    def children(self):
        return tuple(self._generate_children())

    def _generate_children(self):
        # FIXME: make import global
        from turingarena.driver.interface.analysis import TreeAnalyzer
        analyzer = TreeAnalyzer()
        group = []
        for node in self.flat_inner_nodes:
            can_be_grouped = analyzer.can_be_grouped(node)

            if can_be_grouped and len(self._group_directions(group + [node])) <= 1:
                group.append(node)
                continue

            if group:
                yield self._make_step(group)
                group.clear()

            if not can_be_grouped:
                yield node
            else:
                group.append(node)

        if group:
            yield self._make_step(group)

    def _make_step(self, group):
        return Step(tuple(group), self._group_direction(group))

    def _group_direction(self, group):
        directions = self._group_directions(group)
        if not directions:
            return None
        [direction] = directions
        return direction

    def _group_directions(self, group):
        # FIXME: make import global
        from turingarena.driver.interface.analysis import TreeAnalyzer
        analyzer = TreeAnalyzer()
        return {d for n in group for d in analyzer.declaration_directions(n)}

    def _describe_node(self):
        yield "block"
        for n in self.children:
            yield from self._indent_all(n.node_description)


class AbstractContextBlock(AbstractBlock):
    __slots__ = []

    def _generate_flat_inner_nodes(self):
        inner_context = self.context._replace(main_block=False)
        for b in self._get_flat_children_builders():
            node = b(inner_context)
            if not inner_context.is_relevant(node):
                continue
            yield node
            inner_context = inner_context.with_reference_actions(inner_context.reference_actions(node))

    @abstractmethod
    def _get_flat_children_builders(self):
        pass


class Block(AbstractContextBlock, AbstractSyntaxNodeWrapper):
    __slots__ = []

    def _get_flat_children_builders(self):
        for ast in self.ast.statements:
            from turingarena.driver.interface.statements.statements import statement_classes
            for cls in statement_classes[ast.statement_type]:
                if issubclass(cls, AbstractSyntaxNodeWrapper):
                    # still needs context (TODO: remove this distinction)
                    yield partial(cls, ast)
                else:
                    yield lambda context: cls(ast)
