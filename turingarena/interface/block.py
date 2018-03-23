import logging
from collections import OrderedDict

from turingarena.interface.executable import ImperativeStatement
from turingarena.interface.node import AbstractSyntaxNode
from turingarena.interface.statements import compile_statement

logger = logging.getLogger(__name__)


class Block(AbstractSyntaxNode):
    __slots__ = ["ast"]

    @property
    def statements(self):
        return [compile_statement(s) for s in self.ast.statements]

    def declared_variables(self):
        var_statements = [
            compile_statement(s)
            for s in self.ast.statements
            if s.statement_type == "var"
        ]
        return OrderedDict(
            (v.name, v)
            for s in var_statements
            for v in s.variables
        )

    def check_variables(self, initialized_variables, allocated_variables):
        for statement in self.statements:
            initialized_variables += statement.initialized_variables()
            allocated_variables += statement.allocated_variables()
            statement.check_variables(initialized_variables, allocated_variables)


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

    def contextualized_statements(self, context):
        inner_context = context.create_inner()
        for s in self.statements:
            yield s, inner_context
            inner_context = s.update_context(inner_context)
        return inner_context

    def validate(self, context):
        for statement, inner_context in self.contextualized_statements(context):
            statement.validate(inner_context)


ExitCall = object()
