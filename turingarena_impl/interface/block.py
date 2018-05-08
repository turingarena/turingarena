import logging

from turingarena_impl.interface.exceptions import Diagnostic
from turingarena_impl.interface.executable import ImperativeStatement, ImperativeStructure
from turingarena_impl.interface.expressions import SyntheticExpression
from turingarena_impl.interface.parser import AbstractSyntaxNodeWrapper
from turingarena_impl.interface.statement import Statement, SyntheticStatement

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
    def synthetic_statements(self):
        return self.statements

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
        return self.body.declared_variables

    def validate(self):
        from turingarena_impl.interface.control import BreakStatement

        for i, statement in enumerate(self.statements):
            yield from statement.validate()

            if isinstance(statement, BreakStatement):
                if i < len(self.statements) - 1:
                    yield Diagnostic(Diagnostic.Messages.UNREACHABLE_CODE, parseinfo=self.ast.parseinfo)
                    break


class ImperativeBlock(Block, ImperativeStructure):
    __slots__ = []

    @property
    def synthetic_statements(self):
        for s in self.statements:
            yield s
            if (s.statement_type == "call" and # TODO: has callbacks
                    #  self.context.global_context.callbacks
                    True):
                yield SyntheticStatement("write", arguments=[
                    SyntheticExpression("int_literal", value=0),  # no more callbacks
                ])

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
        return self.context
