import logging
from collections import namedtuple

from turingarena import InterfaceExit, InterfaceError
from turingarena.driver.commands import Exit
from turingarena_impl.interface.block import ImperativeBlock
from turingarena_impl.interface.exceptions import Diagnostic
from turingarena_impl.interface.executable import ImperativeStatement, Instruction
from turingarena_impl.interface.expressions import Expression, LiteralExpression
from turingarena_impl.interface.io import ReadStatement
from turingarena_impl.interface.type_expressions import ScalarType
from turingarena_impl.interface.variables import Variable

logger = logging.getLogger(__name__)


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
        return ForIndex(
            variable=Variable(value_type=ScalarType(int), name=self.ast.index),
            range=Expression.compile(self.ast.range, self.context),
        )

    @property
    def body(self):
        return ImperativeBlock(
            ast=self.ast.body,
            context=self.context.create_inner().with_variables((self.index.variable,)),
        )

    def validate(self):
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

    def generate_instructions(self, context):
        while True:
            for instruction in self.body.generate_instructions(context):
                if isinstance(instruction, BreakInstruction):
                    return
                if isinstance(instruction, ContinueInstruction):
                    break  # break from the for and thus continue in the while
                yield instruction

    @property
    def body(self):
        return ImperativeBlock(ast=self.ast.body, context=self.context.with_loop())

    def expects_request(self, request):
        return self.body.expects_request(request)

    def validate(self):
        yield from self.body.validate()

        if not self.body.context_after.has_break:
            yield Diagnostic(Diagnostic.Messages.INFINITE_LOOP, parseinfo=self.ast.parseinfo)

    @property
    def context_after(self):
        return self.body.context_after.with_break(False)


class ContinueStatement(ImperativeStatement):
    def generate_instructions(self, context):
        yield ContinueInstruction()

    def validate(self):
        if not self.context.in_loop:
            yield Diagnostic(Diagnostic.Messages.UNEXPECTED_CONTINUE, parseinfo=self.ast.parseinfo)


class ContinueInstruction(Instruction):
    pass


class BreakStatement(ImperativeStatement):
    def generate_instructions(self, context):
        yield BreakInstruction()

    def validate(self):
        if not self.context.in_loop:
            yield Diagnostic(Diagnostic.Messages.UNEXPECTED_BREAK, parseinfo=self.ast.parseinfo)

    @property
    def context_after(self):
        return self.context.with_break(True)


class BreakInstruction(Instruction):
    pass


class SwitchInstruction(Instruction):
    def __init__(self, switch, condition):
        self.switch = switch
        self.condition = condition

    def on_request_lookahead(self, request):
        if not self.condition.is_resolved():
            for case in self.switch.cases:
                if len(case.labels) == 1 and case.expects_request(request):
                    self.condition.resolve(case.labels[0].value)
                    logger.debug(f"resolved switch condition to {self.condition.get()}")
                    return


class SwitchStatement(ImperativeStatement):
    def generate_instructions(self, context):
        condition = self.variable.evaluate_in(context)

        yield SwitchInstruction(self, condition)

        if not condition.is_resolved():
            raise InterfaceError("Unresolved switch condition")

        value = condition.get()

        for case in self.cases:
            for label in case.labels:
                if value == label.value:
                    yield from case.generate_instructions(context)

    def expects_request(self, request):
        for case in self.cases:
            if case.expects_request(request):
                return True
        return False

    @property
    def cases(self):
        for case in self.ast.cases:
            yield CaseStatement(ast=case, context=self.context)

    @property
    def variable(self):
        return Expression.compile(self.ast.value, self.context)

    def validate(self):
        yield from self.variable.validate()

        cases = [case for case in self.cases]
        if len(cases) == 0:
            yield Diagnostic(Diagnostic.Messages.EMPTY_SWITCH_BODY, parseinfo=self.ast.parseinfo)

        labels = []
        for case in cases:
            for label in case.labels:
                if label in labels:
                    yield Diagnostic(Diagnostic.Messages.DUPLICATED_CASE_LABEL, label, parseinfo=self.ast.parseinfo)
                labels.append(label)
            yield from case.validate()

    @property
    def context_after(self):
        contexts = [case.context_after for case in self.cases]
        if self.default:
            contexts.append(self.default.context_after)
        variables = [ctx.initialized_variables for ctx in contexts]
        initialized_variables = set.intersection(*variables)
        return self.context.with_break(
            any(1 for context in contexts if context.has_break)
        ).with_initialized_variables(initialized_variables)


class CaseStatement(ImperativeStatement):
    def generate_instructions(self, context):
        yield from self.body.generate_instructions(context)

    def expects_request(self, request):
        return self.body.expects_request(request)

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
        return self.body.context_after

    def validate(self):
        for label in self.labels:
            if not isinstance(label, LiteralExpression):
                yield Diagnostic(Diagnostic.Messages.INVALID_CASE_EXPRESSION, parseinfo=self.ast.parseinfo)

