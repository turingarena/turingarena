import logging

from turingarena_impl.interface.block import Block
from turingarena_impl.interface.exceptions import Diagnostic
from turingarena_impl.interface.common import Instruction
from turingarena_impl.interface.statements.statement import Statement


logger = logging.getLogger(__name__)


class LoopStatement(Statement):
    __slots__ = []

    def generate_instructions(self, context):
        while True:
            for instruction in self.body.generate_instructions(context):
                if isinstance(instruction, BreakInstruction):
                    return
                yield instruction

    @property
    def body(self):
        return Block(ast=self.ast.body, context=self.context.with_loop())

    def expects_request(self, request):
        return self.body.expects_request(request)

    def validate(self):
        yield from self.body.validate()

        if not self.body.context_after.has_break:
            yield Diagnostic(Diagnostic.Messages.INFINITE_LOOP, parseinfo=self.ast.parseinfo)

    @property
    def context_after(self):
        return self.body.context_after.with_break(False)


class BreakStatement(Statement):
    __slots__ = []

    def generate_instructions(self, context):
        yield BreakInstruction()

    def validate(self):
        if not self.context.in_loop:
            yield Diagnostic(Diagnostic.Messages.UNEXPECTED_BREAK, parseinfo=self.ast.parseinfo)

    @property
    def context_after(self):
        return self.context.with_break(True)


class BreakInstruction(Instruction):
    pass
