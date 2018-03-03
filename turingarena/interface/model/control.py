from turingarena.common import ImmutableObject
from turingarena.interface.driver.frames import Phase
from turingarena.interface.exceptions import InterfaceExit
from turingarena.interface.model.body import Body, ExitCall
from turingarena.interface.model.expressions import Expression
from turingarena.interface.model.scope import Scope
from turingarena.interface.model.statement import ImperativeStatement
from turingarena.interface.model.type_expressions import ScalarType
from turingarena.interface.model.variables import Variable


class ExitStatement(ImperativeStatement):
    __slots__ = []

    @staticmethod
    def compile(ast, scope):
        return ExitStatement()

    def run(self, context):
        yield from []
        if context.phase == Phase.PREFLIGHT:
            context.engine.ensure_output()
        raise InterfaceExit

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

    def run(self, context):
        condition = context.evaluate(self.condition)
        if context.phase == Phase.PREFLIGHT and not condition.is_resolved():
            # FIXME: use a stricter logic here
            if self.then_body.is_possible_branch(context=context):
                condition.resolve(1)
            else:
                condition.resolve(0)

        if condition.get():
            yield from self.then_body.run(context)
        elif self.else_body is not None:
            yield from self.else_body.run(context)

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

    def run(self, context):
        if context.phase is Phase.RUN or self.may_call():
            size = context.evaluate(self.index.range).get()
            for i in range(size):
                with context.enter(self.scope) as inner_context:
                    inner_context.frame[self.index.variable] = i
                    yield from self.body.run(inner_context)

    def may_call(self):
        return any(f is not None for f in self.body.first_calls())

    def first_calls(self):
        return self.body.first_calls() | {None}


class LoopStatement(ImperativeStatement):
    __slots__ = ["body"]

    @staticmethod
    def compile(ast, scope):
        return LoopStatement(
            body=Body.compile(ast.body, scope=scope),
        )

    def run(self, context):
        if context.phase is Phase.RUN or self.may_call():
            size = context.evaluate(self.index.range).get()
            for i in range(size):
                with context.enter(self.scope) as inner_context:
                    inner_context.frame[self.index.variable] = i
                    yield from self.body.run(inner_context)

    def first_calls(self):
        return self.body.first_calls() | {None}
