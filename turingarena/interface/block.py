import logging
from collections import OrderedDict

from turingarena.interface.context import StaticContext
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

    def is_possible_branch(self, *, context):
        request = context.engine.peek_request()
        if request.message_type == "function_call":
            call = request.function_name
        elif request.message_type == "exit":
            call = ExitCall
        else:
            call = None
        return call is not None and call in self.first_calls()

    def first_calls(self):
        ans = {None}
        for s in self.statements:
            if not isinstance(s, ImperativeStatement):
                continue
            if None not in ans:
                break
            ans.remove(None)
            ans.update(s.first_calls())
        return ans

    def contextualized_statements(self, context):
        inner_context = StaticContext(
            callbacks=context.callbacks,
            global_variables=context.global_variables,
            functions=context.functions,
            variables=context.variables,
        )
        for s in self.statements:
            yield s, inner_context
            inner_context = s.update_context(inner_context)
        return inner_context

    def validate(self, context):
        for statement, inner_context in self.contextualized_statements(context):
            statement.validate(inner_context)


ExitCall = object()
