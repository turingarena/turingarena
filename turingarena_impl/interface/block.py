import logging
from collections import namedtuple

from turingarena_impl.interface.common import ImperativeStructure, AbstractSyntaxNodeWrapper, Instruction
from turingarena_impl.interface.diagnostics import Diagnostic
from turingarena_impl.interface.expressions import SyntheticExpression, VariableReference, ArrayItemReference
from turingarena_impl.interface.statements.statement import Statement, SyntheticStatement

logger = logging.getLogger(__name__)


class Block(ImperativeStructure, AbstractSyntaxNodeWrapper):
    __slots__ = []

    def _generate_statements(self):
        inner_context = self.inner_context_at_begin
        for s in self.ast.statements:
            statement = Statement.compile(s, inner_context)
            inner_context = statement.context_after
            yield statement

    @property
    def statements(self):
        return list(self._generate_statements())

    @property
    def inner_context_at_begin(self):
        return self.context.create_inner()

    @property
    def inner_context_at_end(self):
        if self.statements:
            return self.statements[-1].context_after
        else:
            return self.inner_context_at_begin

    @property
    def declared_variables(self):
        return tuple(
            var
            for stmt in self.statements
            for var in stmt.declared_variables
        )

    def validate(self):
        from turingarena_impl.interface.statements.loop import BreakStatement
        from turingarena_impl.interface.statements.exit import ExitStatement

        for i, statement in enumerate(self.statements):
            yield from statement.validate()
            if isinstance(statement, BreakStatement) or isinstance(statement, ExitStatement):
                if i < len(self.statements) - 1:
                    yield Diagnostic(Diagnostic.Messages.UNREACHABLE_CODE, parseinfo=self.ast.parseinfo)
                    break

    @property
    def synthetic_statements(self):
        for s in self.statements:
            yield s
            if s.statement_type == "call" and s.function.has_callbacks:
                yield SyntheticStatement("write", arguments=[
                    SyntheticExpression("int_literal", value=0),  # no more callbacks
                ])

    def generate_instructions(self, bindings):
        inner_bindings = {
            **{
                var.name: [None] for var in self.declared_variables
            },
            **bindings,
        }
        for statement in self.statements:
            # FIXME
            # for allocation in statement.variables_to_allocate:
            #    yield AllocationInstruction(allocation, inner_bindings)
            yield from statement.generate_instructions(inner_bindings)

    def expects_request(self, request):
        for s in self.statements:
            if not isinstance(s, Statement):
                continue
            if s.expects_request(request):
                return True
            if not s.expects_request(None):
                break

    @property
    def may_process_requests(self):
        return any(
            s.may_process_requests
            for s in self.statements
        )

    @property
    def context_after(self):
        return self.context


class AllocationInstruction(Instruction, namedtuple("AllocationInstruction", [
    "allocation", "bindings"
])):
    # FIXME: downward or upward? should be implemented differently (say, in for loops)

    def has_downward(self):
        return True

    def on_communicate_downward(self, lines):
        logger.debug(f"ALLOCATION: {self}")
        ref = VariableReference(name=self.allocation.name, bindings=self.bindings)
        for index in self.allocation.indexes:
            index_ref = VariableReference(name=index, bindings=self.bindings)
            ref = ArrayItemReference(ref.get(), index_ref.get())
        ref.set([None] * self.allocation.size.evaluate(self.bindings))
