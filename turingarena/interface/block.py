import logging
from collections import OrderedDict
from functools import lru_cache

from turingarena.interface.executable import ImperativeStatement, ImperativeStructure
from turingarena.interface.node import AbstractSyntaxNodeWrapper
from turingarena.interface.statement import Statement

logger = logging.getLogger(__name__)


class Block(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @property
    def statements(self):
        statements = []
        inner_context = self.context.create_inner()
        for s in self.ast.statements:
            statement = Statement.compile(s, inner_context)
            inner_context = statement.context_after
            statements.append(statement)
        return statements

    @property
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
        inner_context = context.child(self.declared_variables)
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
        if not self.statements:
            return self.context
        statement_ctx = self.statements[-1].context_after
        return self.context.with_initialized_variables({
            variable
            for variable in statement_ctx.initialized_variables
            if variable in self.context.variables
        }).with_allocated_variables({
            variable
            for variable in statement_ctx.allocated_variables
            if variable in self.context.variables
        }).with_flushed_output(statement_ctx.has_flushed_output)
