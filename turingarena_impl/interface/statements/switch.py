import logging

from turingarena import InterfaceError
from turingarena_impl.interface.block import Block
from turingarena_impl.interface.common import Instruction
from turingarena_impl.interface.exceptions import Diagnostic
from turingarena_impl.interface.expressions import Expression
from turingarena_impl.interface.statements.statement import Statement

logger = logging.getLogger(__name__)


class SwitchStatement(Statement):
    __slots__ = []

    def generate_instructions(self, bindings):
        condition = self.variable.evaluate_in(bindings)

        yield SwitchInstruction(self, condition)

        if not condition.is_resolved():
            raise InterfaceError("Unresolved switch condition")

        value = condition.get()

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
        return Expression.compile(self.ast.value, self.context)

    def validate(self):
        yield from self.variable.validate()

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

    @property
    def context_after(self):
        return self.body.context_after


class SwitchInstruction(Instruction):
    def __init__(self, switch, condition):
        self.switch = switch
        self.condition = condition

    def on_request_lookahead(self, request):
        if not self.condition.is_resolved():
            for case in self.switch.cases:
                if len(case.labels) == 1 and case.expects_request(request):
                    self.condition.resolve(case.labels[0].value)
                    return


