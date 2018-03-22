from turingarena.common import ImmutableObject
from turingarena.interface.body import Body, ExitCall
from turingarena.interface.driver.commands import Exit
from turingarena.interface.exceptions import InterfaceExit
from turingarena.interface.executable import ImperativeStatement, Instruction
from turingarena.interface.expressions import Expression
from turingarena.interface.scope import Scope
from turingarena.interface.type_expressions import ScalarType
from turingarena.interface.variables import Variable


class ExitStatement(ImperativeStatement):
    __slots__ = []

    @staticmethod
    def compile(ast, scope):
        return ExitStatement(ast=ast)

    def generate_instructions(self, context):
        yield ExitInstruction()
        raise InterfaceExit

    def first_calls(self):
        return {ExitCall}


class ExitInstruction(Instruction):
    __slots__ = []

    def on_request_lookahead(self, request):
        assert isinstance(request, Exit)

    def on_generate_response(self):
        return []


class IfStatement(ImperativeStatement):
    __slots__ = ["condition", "then_body", "else_body"]

    @staticmethod
    def compile(ast, scope):
        return IfStatement(
            ast=ast,
            condition=Expression.compile(ast.condition, scope=scope),
            then_body=Body.compile(ast.then_body, scope=scope),
            else_body=(
                None if ast.else_body is None else
                Body.compile(ast.then_body, scope=scope)
            ),
        )

    def generate_instructions(self, context):
        condition = self.condition.evaluate_in(context)
        if not condition.is_resolved():
            # FIXME: use a stricter logic here
            if self.then_body.is_possible_branch(context):
                condition.resolve(1)
            else:
                condition.resolve(0)

        if condition.get():
            yield from self.then_body.generate_instructions(context)
        elif self.else_body is not None:
            yield from self.else_body.generate_instructions(context)

    def check_variables(self, initialized_variables, allocated_variables):
        self.condition.check_variables(initialized_variables, allocated_variables)
        self.then_body.check_variables(initialized_variables, allocated_variables)
        if self.else_body:
            self.else_body.check_variables(initialized_variables, allocated_variables)

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
            ast=ast,
            index=ForIndex(
                variable=index_var,
                range=Expression.compile(ast.index.range, scope=scope),
            ),
            body=Body.compile(ast.body, scope=for_scope),
            scope=for_scope,
        )

    def generate_instructions(self, context):
        if not self.may_call():
            yield SimpleForInstruction(statement=self, context=context)
        else:
            yield from self.do_generate_instruction(context)

    def do_generate_instruction(self, context):
        size = self.index.range.evaluate_in(context=context).get()
        for i in range(size):
            inner_context = context.child(self.scope)
            inner_context.bindings[self.index.variable] = i
            yield from self.body.generate_instructions(inner_context)

    def initialized_variables(self):
        return [self.index.variable]

    def may_call(self):
        return any(f is not None for f in self.body.first_calls())

    def check_variables(self, initialized_variables, allocated_variables):
        self.body.check_variables(initialized_variables, allocated_variables)

    def first_calls(self):
        return self.body.first_calls() | {None}


class SimpleForInstruction(Instruction):
    """
    Corresponds to a for-loop which does not perform any function call.
    This is seen as a single instruction so that it can be fully skipped
    in the preflight phase, when the number of iterations is not yet known.
    """

    __slots__ = ["statement", "context"]

    def on_communicate_with_process(self, connection):
        for instruction in self.statement.do_generate_instruction(self.context):
            instruction.on_communicate_with_process(connection)


class LoopStatement(ImperativeStatement):
    __slots__ = ["body"]

    @staticmethod
    def compile(ast, scope):
        return LoopStatement(
            ast=ast,
            body=Body.compile(ast.body, scope=scope),
        )

    def first_calls(self):
        return self.body.first_calls() | {None}
