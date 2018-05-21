import logging

from turingarena_impl.interface.block import Block
from turingarena_impl.interface.diagnostics import Diagnostic
from turingarena_impl.interface.statements.statement import Statement

logger = logging.getLogger(__name__)


class LoopStatement(Statement):
    __slots__ = []

    def generate_instructions(self, bindings):
        while True:
            for instruction in self.body.generate_instructions(bindings):
                if instruction is BREAK_SENTINEL:
                    break
                yield instruction

    @property
    def body(self):
        return Block(ast=self.ast.body, context=self.context.with_loop())

    def expects_request(self, request):
        return self.body.expects_request(request)

    def validate(self):
        yield from self.body.validate()

    @property
    def may_process_requests(self):
        return True


class BreakStatement(Statement):
    __slots__ = []

    def generate_instructions(self, bindings):
        yield BREAK_SENTINEL

    def validate(self):
        if not self.context.in_loop:
            yield Diagnostic(Diagnostic.Messages.UNEXPECTED_BREAK, parseinfo=self.ast.parseinfo)


BREAK_SENTINEL = object()
