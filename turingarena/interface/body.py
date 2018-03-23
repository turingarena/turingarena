import logging

from turingarena.interface.context import StaticContext
from turingarena.interface.executable import ImperativeStatement
from turingarena.interface.node import AbstractSyntaxNode
from turingarena.interface.scope import Scope
from turingarena.interface.statements import compile_statement
from turingarena.interface.variables import VarStatement

logger = logging.getLogger(__name__)


class Body(AbstractSyntaxNode):
    __slots__ = ["ast", "statements", "scope"]

    @staticmethod
    def compile(ast, *, scope):
        scope = Scope(scope)

        statements = list(Body.generate_statements(ast, scope))

        return Body(
            ast=ast,
            scope=scope,
            statements=statements
        )

    @staticmethod
    def generate_statements(ast, scope):
        for s in ast.statements:
            compiled_s = compile_statement(s, scope=scope)
            if isinstance(compiled_s, VarStatement):
                for v in compiled_s.declared_variables():
                    scope.variables[v.name] = v
            yield compiled_s

    def contextualized_statements(self, context):
        for s in self.statements:
            yield s, StaticContext(
                scope=self.scope,
                global_variables=context.global_variables,
            )

    def check_variables(self, initialized_variables, allocated_variables):
        for statement in self.statements:
            initialized_variables += statement.initialized_variables()
            allocated_variables += statement.allocated_variables()
            statement.check_variables(initialized_variables, allocated_variables)

    def generate_instructions(self, context):
        inner_context = context.child(self.scope)
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


ExitCall = object()
