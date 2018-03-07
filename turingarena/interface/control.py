from turingarena.common import ImmutableObject
from turingarena.interface.body import Body, ExitCall
from turingarena.interface.exceptions import InterfaceExit
from turingarena.interface.executable import ImperativeStatement, StatementInstruction, Instruction
from turingarena.interface.expressions import Expression
from turingarena.interface.scope import Scope
from turingarena.interface.type_expressions import ScalarType
from turingarena.interface.variables import Variable


class ExitStatement(ImperativeStatement):
    __slots__ = []

    @staticmethod
    def compile(ast, scope):
        return ExitStatement()

    def unroll(self, frame):
        yield StatementInstruction(statement=self, frame=frame)
        raise InterfaceExit

    def run_driver_pre(self, request, *, frame):
        assert request.request_type == "exit"

    def run_driver_post(self, *, frame):
        return []

    def first_calls(self):
        return {ExitCall}


class IfStatement(ImperativeStatement):
    __slots__ = ["condition", "then_body", "else_body"]

    @staticmethod
    def compile(ast, scope):
        return IfStatement(
            condition=Expression.compile(ast.condition, scope=scope),
            then_body=Body.compile(ast.then_body, scope=scope),
            else_body=(
                None if ast.else_body is None else
                Body.compile(ast.then_body, scope=scope)
            ),
        )

    def unroll(self, frame):
        condition = self.condition.evaluate_in(frame)
        if not condition.is_resolved():
            # FIXME: use a stricter logic here
            if self.then_body.is_possible_branch(frame):
                condition.resolve(1)
            else:
                condition.resolve(0)

        if condition.get():
            yield from self.then_body.unroll(frame)
        elif self.else_body is not None:
            yield from self.else_body.unroll(frame)

    def first_calls(self):
        return self.then_body.first_calls() | (
            {None} if self.else_body is not None else
            self.else_body.first_calls()
        )


class ForIndex(ImmutableObject):
    __slots__ = ["variable", "range"]


class ForStatement(ImperativeStatement):
    __slots__ = ["index", "body", "scope"]

    @staticmethod
    def compile(ast, scope):
        for_scope = Scope(scope)
        index_var = Variable(value_type=ScalarType(int), name=ast.index.declarator.name)
        for_scope.variables[index_var.name] = index_var
        return ForStatement(
            index=ForIndex(
                variable=index_var,
                range=Expression.compile(ast.index.range, scope=scope),
            ),
            body=Body.compile(ast.body, scope=for_scope),
            scope=for_scope,
        )

    def unroll(self, frame):
        if not self.may_call():
            yield SimpleForInstruction(statement=self, frame=frame)
        else:
            yield from self.do_unroll(frame)

    def do_unroll(self, frame):
        size = self.index.range.evaluate_in(frame=frame).get()
        for i in range(size):
            with frame.child(self.scope) as inner_frame:
                inner_frame[self.index.variable] = i
                yield from self.body.unroll(inner_frame)

    def may_call(self):
        return any(f is not None for f in self.body.first_calls())

    def first_calls(self):
        return self.body.first_calls() | {None}


class SimpleForInstruction(Instruction):
    """
    Corresponds to a for-loop which does not perform any function call.
    This is seen as a single instruction so that it can be fully skipped
    in the preflight phase, when the number of iterations is not yet known.
    """

    __slots__ = ["statement", "frame"]

    def run_sandbox(self, connection):
        for instruction in self.statement.do_unroll(self.frame):
            instruction.run_sandbox(connection)


class LoopStatement(ImperativeStatement):
    __slots__ = ["body"]

    @staticmethod
    def compile(ast, scope):
        return LoopStatement(
            body=Body.compile(ast.body, scope=scope),
        )

    def first_calls(self):
        return self.body.first_calls() | {None}
