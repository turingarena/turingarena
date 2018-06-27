import logging
import warnings

from turingarena_impl.driver.interface.block import Block, BlockNode
from turingarena_impl.driver.interface.common import AbstractSyntaxNodeWrapper
from turingarena_impl.driver.interface.diagnostics import Diagnostic
from turingarena_impl.driver.interface.expressions import Expression
from turingarena_impl.driver.interface.nodes import StatementIntermediateNode, IntermediateNode, RequestLookaheadNode
from turingarena_impl.driver.interface.statements.statement import Statement
from turingarena_impl.driver.interface.variables import ReferenceStatus, ReferenceAction

logger = logging.getLogger(__name__)


class SwitchStatement(Statement, IntermediateNode):
    __slots__ = []

    def _get_intermediate_nodes(self):
        if self._should_resolve():
            if not self.context.has_request_lookahead:
                yield RequestLookaheadNode()
            yield SwitchResolveNode(self)
        # TODO: resolution node
        yield self

    def _should_resolve(self):
        return self.value.reference is not None and not self.value.is_status(ReferenceStatus.RESOLVED)

    def _get_has_request_lookahead(self):
        return self.context.has_request_lookahead or self._should_resolve()

    def _get_declaration_directions(self):
        for c in self.cases:
            yield from c.body_node.declaration_directions

    def _get_reference_actions(self):
        for c in self.cases:
            yield from c.body_node.reference_actions

    def _driver_run(self, context):
        value = self.value.evaluate(context.bindings)

        for case in self.cases:
            for label in case.labels:
                if value == label.value:
                    return case.body_node.driver_run(context)

    def expects_request(self, request):
        for case in self.cases:
            if case.expects_request(request):
                return True
        return False

    @property
    def cases(self):
        return list(self._get_cases())

    def _get_cases(self):
        for case in self.ast.cases:
            # FIXME: .with_reference_actions(<resolve node>.reference_actions)
            yield CaseStatement(ast=case, context=self.context._replace(
                has_request_lookahead=self.has_request_lookahead,
            ))

    @property
    def variable(self):
        warnings.warn("use value", DeprecationWarning)
        return self.value

    @property
    def value(self):
        return Expression.compile(self.ast.value, self.context.expression())

    def validate(self):
        yield from self.value.validate()

        cases = [case for case in self.cases]
        if len(cases) == 0:
            yield Diagnostic(Diagnostic.Messages.EMPTY_SWITCH_BODY, parseinfo=self.ast.parseinfo)

        labels = []
        for case in cases:
            for label in case.labels:
                if label in labels:
                    yield Diagnostic(Diagnostic.Messages.DUPLICATED_CASE_LABEL, label, parseinfo=self.ast.parseinfo)
                labels.append(label)
            yield from case.validate()

    def _describe_node(self):
        yield f"switch {self.value} "
        for c in self.cases:
            yield from self._indent_all(self._describe_case(c))

    def _describe_case(self, case):
        labels = ", ".join(case.labels)
        yield f"case {labels}"
        yield from self._indent_all(case.body_node.node_description)


class CaseStatement(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def body(self):
        return Block(ast=self.ast.body, context=self.context)

    @property
    def body_node(self):
        return BlockNode.from_nodes(self.body.flat_inner_nodes)

    @property
    def labels(self):
        return self.ast.labels

    def validate(self):
        yield from self.body.validate()


class SwitchResolveNode(StatementIntermediateNode):
    def _get_reference_actions(self):
        yield ReferenceAction(self.statement.value.reference, ReferenceStatus.RESOLVED)

    def _driver_run(self, context):
        pass  # TODO

    def _describe_node(self):
        yield f"resolve {self.statement}"


class SwitchInstruction(StatementIntermediateNode):
    def on_request_lookahead(self, request):
        if self.statement.value.is_assignable():
            for case in self.statement.cases:
                if len(case.labels) == 1 and case.expects_request(request):
                    self.statement.value.assign(self.bindings, case.labels[0].value)
                    return
