import logging
from collections import OrderedDict

from turingarena.interface.executable import ImperativeStatement, ImperativeStructure
from turingarena.interface.node import AbstractSyntaxNodeWrapper
from turingarena.interface.statement import Statement
from turingarena.interface.exceptions import Diagnostic

logger = logging.getLogger(__name__)


class Block(AbstractSyntaxNodeWrapper):
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
        return OrderedDict(
            (v.name, v)
            for s in self.statements
            if s.statement_type == "var"
            for v in s.variables
        )

    def validate(self):
        from turingarena.interface.control import ContinueStatement, BreakStatement

        for i, statement in enumerate(self.statements):
            yield from statement.validate()

            if isinstance(statement, ContinueStatement) or isinstance(statement, BreakStatement):
                if i < len(self.statements) - 1:
                    yield Diagnostic(Diagnostic.Messages.UNREACHABLE_CODE, parseinfo=self.ast.parseinfo)
                    break


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
        inner_context = self.inner_context_at_end
        return self.context.with_initialized_variables({
            variable
            for variable in inner_context.initialized_variables
            if variable in self.context.variables
        }).with_allocated_variables({
            variable
            for variable in inner_context.allocated_variables
            if variable and variable[0] in self.context.variables
        }).with_flushed_output(inner_context.has_flushed_output).with_break(
            inner_context.has_break
        )
