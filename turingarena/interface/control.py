from collections import namedtuple

from turingarena.interface.block import ImperativeBlock
from turingarena.interface.driver.commands import Exit
from turingarena.interface.exceptions import InterfaceExit, Diagnostic
from turingarena.interface.executable import ImperativeStatement, Instruction
from turingarena.interface.expressions import Expression, LiteralExpression
from turingarena.interface.io import FlushStatement, ReadStatement
from turingarena.interface.type_expressions import ScalarType
from turingarena.interface.variables import Variable


class ExitStatement(ImperativeStatement):
    __slots__ = []

    def generate_instructions(self, context):
        yield ExitInstruction()
        raise InterfaceExit

    def validate(self):
        # TODO: check that exit is used only in valid places
        return []

    def expects_request(self, request):
        return request is not None and request.request_type == "exit"


class ExitInstruction(Instruction):
    __slots__ = []

    def on_request_lookahead(self, request):
        assert isinstance(request, Exit)

    def on_generate_response(self):
        return []


class IfStatement(ImperativeStatement):
    __slots__ = []

    @property
    def condition(self):
        return Expression.compile(self.ast.condition, self.context)

    @property
    def then_body(self):
        return ImperativeBlock(self.ast.then_body, self.context)

    @property
    def else_body(self):
        if self.ast.else_body is None:
            return None
        return ImperativeBlock(self.ast.else_body, self.context)

    def validate(self):
        yield from self.condition.validate()
        yield from self.then_body.validate()
        if self.else_body:
            yield from self.else_body.validate()

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

    def expects_request(self, request):
        return (
            self.then_body.expects_request(request) or
            self.else_body is not None and self.else_body.expects_request(request)
        )

    @property
    def context_after(self):
        initialized_variables = {
            var
            for var in self.then_body.context_after.initialized_variables
            if not self.else_body or var in self.else_body.context_after.initialized_variables
        }
        allocated_variable = {
            var
            for var in self.then_body.context_after.allocated_variables
            if not self.else_body or var in self.else_body.context_after.allocated_variables
        }
        has_flush = self.then_body.context_after.has_flushed_output and (not self.else_body or self.else_body.context_after.has_flushed_output)
        return self.context.with_initialized_variables(initialized_variables)\
            .with_allocated_variables(allocated_variable).with_flushed_output(has_flush)


ForIndex = namedtuple("ForIndex", ["variable", "range"])


class ForStatement(ImperativeStatement):
    __slots__ = []

    @property
    def index(self):
        ast = self.ast.index
        return ForIndex(
            variable=Variable(value_type=ScalarType(int), name=ast.declarator.name),
            range=Expression.compile(ast.range, self.context),
        )

    @property
    def body(self):
        return ImperativeBlock(
            ast=self.ast.body,
            context=self.context.create_inner().with_index_variable(self.index),
        )

    def validate(self):
        if not self.body.context_after.has_flushed_output:
            for statement in self.body.statements:
                if isinstance(statement, FlushStatement):
                    break
                if isinstance(statement, ReadStatement):
                    yield Diagnostic("missing flush between write and read instructions", parseinfo=self.ast.parseinfo)
        yield from self.body.validate()

    def generate_instructions(self, context):
        if self.body.expects_request(None):
            yield SimpleForInstruction(statement=self, context=context)
        else:
            yield from self.do_generate_instruction(context)

    def do_generate_instruction(self, context):
        size = self.index.range.evaluate_in(context=context).get()
        for i in range(size):
            inner_context = context.child({self.index.variable.name: self.index.variable})
            inner_context.bindings[self.index.variable] = i
            yield from self.body.generate_instructions(inner_context)

    @property
    def context_after(self):
        return self.body.context_after

    def expects_request(self, request):
        return (
            request is None
            or self.body.expects_request(request)
        )


class SimpleForInstruction(Instruction, namedtuple("SimpleForInstruction", [
    "statement", "context"
])):
    """
    Corresponds to a for-loop which does not perform any function call.
    This is seen as a single instruction so that it can be fully skipped
    in the preflight phase, when the number of iterations is not yet known.
    """

    __slots__ = []

    def on_communicate_with_process(self, connection):
        for instruction in self.statement.do_generate_instruction(self.context):
            instruction.on_communicate_with_process(connection)


class LoopStatement(ImperativeStatement):
    __slots__ = []

    @property
    def body(self):
        return ImperativeBlock(ast=self.ast.body, context=self.context.with_loop())

    def expects_request(self, request):
        return self.body.expects_request(request)

    def validate(self):
        yield from self.body.validate()

        # TODO: check that the loop {} terminates

    @property
    def context_after(self):
        return self.body.context_after


class ContinueStatement(ImperativeStatement):
    def generate_instructions(self, context):
        return ContinueInstruction()

    def validate(self):
        def validate(self):
            if not self.context.in_loop:
                yield Diagnostic(Diagnostic.Message.UNEXPECTED_BREAK)


class ContinueInstruction(Instruction):
    pass


class BreakStatement(ImperativeStatement):
    def generate_instructions(self, context):
        return BreakInstruction()

    def validate(self):
        if not self.context.in_loop:
            yield Diagnostic(Diagnostic.Message.UNEXPECTED_CONTINUE)


class BreakInstruction(Instruction):
    pass


class SwitchStatement(ImperativeStatement):
    def generate_instructions(self, context):
        return SwitchInstruction()

    @property
    def cases(self):
        for case in self.ast.cases:
            yield CaseStatement(ast=case, context=self.context)

    @property
    def variable(self):
        return Expression.compile(self.ast.value, self.context)

    @property
    def default(self):
        return ImperativeBlock(ast=self.ast.default.body, context=self.context) if self.ast.default else None

    def validate(self):
        yield from self.variable.validate()

        cases = [case for case in self.cases]
        if len(cases) == 0:
            yield Diagnostic(Diagnostic.Messages.EMPTY_SWITCH_BODY, parseinfo=self.ast.parseinfo)

        for case in cases:
            yield from case.validate()

    @property
    def context_after(self):
        # TODO: think what context after to return

        return self.context


class SwitchInstruction(Instruction):
    pass


class CaseStatement(ImperativeStatement):
    def generate_instructions(self, context):
        return CaseInstruction()

    @property
    def body(self):
        return ImperativeBlock(ast=self.ast.body, context=self.context)

    @property
    def labels(self):
        return [
            Expression.compile(label, self.context)
            for label in self.ast.labels
        ]

    @property
    def context_after(self):
        return self.body.context

    def validate(self):
        for label in self.labels:
            if not isinstance(label, LiteralExpression):
                yield Diagnostic(Diagnostic.Messages.INVALID_CASE_EXPRESSION, parseinfo=self.ast.parseinfo)


class CaseInstruction(Instruction):
    pass
