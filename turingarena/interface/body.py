import logging

from turingarena.interface.executable import ImperativeStatement
from turingarena.interface.node import AbstractSyntaxNode
from turingarena.interface.scope import Scope
from turingarena.interface.statements import compile_statement

logger = logging.getLogger(__name__)


class Body(AbstractSyntaxNode):
    __slots__ = ["statements", "scope"]

    @staticmethod
    def compile(ast, *, scope):
        scope = Scope(scope)
        statements = [
            compile_statement(s, scope=scope)
            for s in ast.statements
        ]
        return Body(
            scope=scope,
            statements=statements
        )

    def unroll(self, frame):
        logger.debug(f"unrolling body {self!s:.50}")
        with frame.child(self.scope) as inner_frame:
            for statement in self.statements:
                if not isinstance(statement, ImperativeStatement):
                    continue
                yield from statement.unroll(inner_frame)

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
            if None not in ans:
                break
            ans.remove(None)
            ans.update(s.first_calls())
        return ans


ExitCall = object()
