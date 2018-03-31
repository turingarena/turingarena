import logging
from collections import OrderedDict

from turingarena.interface.executable import ImperativeStatement, ImperativeStructure
from turingarena.interface.node import AbstractSyntaxNodeWrapper
from turingarena.interface.statements import compile_statement

logger = logging.getLogger(__name__)


class Block(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def statements(self):
        inner_context = self.context.create_inner()
        for s in self.ast.statements:
            statement = compile_statement(s, inner_context)
            yield statement
            inner_context = statement.context_after

    def declared_variables(self):
        return OrderedDict(
            (v.name, v)
            for s in self.statements
            if s.statement_type == "var"
            for v in s.variables
        )

    def validate(self):
        for statement in self.statements:
            yield from statement.validate()


class ImperativeBlock(Block, ImperativeStructure):
    __slots__ = []

    def generate_instructions(self, context):
        inner_context = context.child(self.declared_variables())
        for statement in self.statements:
            if isinstance(statement, ImperativeStatement):
                yield from statement.generate_instructions(inner_context)

    def expects_request(self, request):
        for s in self.statements:
            if not isinstance(s, ImperativeStatement):
                continue
            if s.expects_request(request):
                return True
            if not s.expects_request(None):
                break

    @property
    def context_after(self):
        statements = [s for s in self.statements]
        if not statements:
            return self.context
        statement_ctx = statements[-1].context_after
        return self.context.with_initialized_variables({
            variable
            for variable in statement_ctx.initialized_variables
            if variable in self.context.variables
        }).with_allocated_variables({
            variable
            for variable in statement_ctx.allocated_variables
            if variable in self.context.variables
        }).with_flushed_output(statement_ctx.has_flushed_output)


ExitCall = object()
