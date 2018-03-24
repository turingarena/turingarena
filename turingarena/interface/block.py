import logging
from collections import OrderedDict

from turingarena.interface.executable import ImperativeStatement
from turingarena.interface.node import AbstractSyntaxNode
from turingarena.interface.statements import compile_statement

logger = logging.getLogger(__name__)


class Block(AbstractSyntaxNode):
    __slots__ = ["ast", "context"]

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

    def check_variables(self, initialized_variables, allocated_variables):
        for statement in self.statements:
            initialized_variables += statement.initialized_variables()
            allocated_variables += statement.allocated_variables()
            statement.check_variables(initialized_variables, allocated_variables)

    def validate(self):
        for statement in self.statements:
            statement.validate()


class ImperativeBlock(Block):
    __slots__ = []

    def generate_instructions(self, context):
        inner_context = context.child(self.declared_variables())
        for statement in self.statements:
            if not isinstance(statement, ImperativeStatement):
                continue
            yield from statement.generate_instructions(inner_context)

    def expects_request(self, request):
        for s in self.statements:
            if s.expects_request(request):
                return True
            if not s.expects_request(None):
                break


ExitCall = object()
