import logging
import warnings

from turingarena.driver.interface.block import Block
from turingarena.driver.interface.common import AbstractSyntaxNodeWrapper
from turingarena.driver.interface.diagnostics import Diagnostic
from turingarena.driver.interface.expranalysis import ExpressionStatusAnalyzer
from turingarena.driver.interface.expressions import Expression, IntLiteral
from turingarena.driver.interface.nodes import IntermediateNode
from turingarena.driver.interface.statements.statement import Statement
from turingarena.driver.interface.stmtanalysis import StatementAnalyzer
from turingarena.driver.interface.variables import ReferenceStatus, ReferenceAction

logger = logging.getLogger(__name__)


class SwitchNode(IntermediateNode, AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def cases(self):
        return tuple(self._get_cases())

    def _get_cases(self):
        for case in self.ast.cases:
            # FIXME: .with_reference_actions(<resolve node>.reference_actions)
            yield Case(ast=case, context=self.context)

    @property
    def variable(self):
        warnings.warn("use value", DeprecationWarning)
        return self.value

    @property
    def value(self):
        return Expression.compile(self.ast.value, self.context.expression())


class Switch(SwitchNode, Statement):
    __slots__ = []

    def _get_declaration_directions(self):
        for c in self.cases:
            yield from c.body.declaration_directions

    def _get_reference_actions(self):
        for c in self.cases:
            yield from c.body.reference_actions

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
        labels = ", ".join(str(l.value) for l in case.labels)
        yield f"case {labels}"
        yield from self._indent_all(case.body.node_description)


class Case(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def body(self):
        return Block(ast=self.ast.body, context=self.context)

    @property
    def labels(self):
        return [
            Expression.compile(l, self.context.expression())
            for l in self.ast.labels
        ]

    def validate(self):
        for l in self.labels:
            if not isinstance(l, IntLiteral):
                yield Diagnostic(
                    Diagnostic.Messages.SWITCH_LABEL_NOT_LITERAL,
                    parseinfo=self.ast.labels.parseinfo,
                )
        yield from self.body.validate()


class SwitchResolve(SwitchNode):
    def _is_already_resolved(self):
        return ExpressionStatusAnalyzer(self.context, ReferenceStatus.RESOLVED).visit(self.value)

    def _is_relevant(self):
        return not self._is_already_resolved()

    def _get_reference_actions(self):
        yield ReferenceAction(self.value.reference, ReferenceStatus.RESOLVED)

    def get_matching_cases(self, request):
        return list(self._find_matching_cases(request))

    def _find_matching_cases(self, request):
        matching_cases_requests = list(self._find_cases_expecting(request))
        if matching_cases_requests:
            return matching_cases_requests
        else:
            return list(self._find_cases_expecting(None))

    def _find_cases_expecting(self, request):
        for c in self.cases:
            if request in StatementAnalyzer().first_requests(c.body):
                yield c

    def _describe_node(self):
        yield f"resolve {self}"
