import logging
import warnings
from collections import namedtuple

from turingarena_impl.interface.block import Block
from turingarena_impl.interface.common import Instruction
from turingarena_impl.interface.diagnostics import Diagnostic
from turingarena_impl.interface.expressions import Expression
from turingarena_impl.interface.statements.statement import Statement

logger = logging.getLogger(__name__)


class SwitchStatement(Statement):
    __slots__ = []

    def generate_instructions(self, bindings):
        yield SwitchInstruction(self, bindings)

        value = self.value.evaluate(bindings)

        for case in self.cases:
            for label in case.labels:
                if value == label.value:
                    yield from case.generate_instructions(bindings)

    def expects_request(self, request):
        for case in self.cases:
            if case.expects_request(request):
                return True
        return False

    @property
    def cases(self):
        for case in self.ast.cases:
            yield CaseStatement(ast=case, context=self.context)

    @property
    def variable(self):
        warnings.warn("use value", DeprecationWarning)
        return self.value

    @property
    def value(self):
        return Expression.compile(self.ast.value, self.context)

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

    @property
    def may_process_requests(self):
        return any(
            case.body.may_process_requests
            for case in self.cases
        )


class CaseStatement(Statement):
    __slots__ = []

    def generate_instructions(self, bindings):
        yield from self.body.generate_instructions(bindings)

    def expects_request(self, request):
        return self.body.expects_request(request)

    @property
    def body(self):
        return Block(ast=self.ast.body, context=self.context)

    @property
    def labels(self):
        return self.ast.labels


class SwitchInstruction(Instruction, namedtuple("SwitchInstruction", ["statement", "bindings"])):
    def on_request_lookahead(self, request):
        if self.statement.value.is_assignable():
            for case in self.statement.cases:
                if len(case.labels) == 1 and case.expects_request(request):
                    self.statement.value.assign(self.bindings, case.labels[0].value)
                    return
