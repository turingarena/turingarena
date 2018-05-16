import logging
from collections import namedtuple

from turingarena_impl.interface.block import Block
from turingarena_impl.interface.common import Instruction
from turingarena_impl.interface.expressions import Expression
from turingarena_impl.interface.statements.statement import Statement
from turingarena_impl.interface.variables import Variable, ScalarType, VariableDeclaration, VariableAllocation

logger = logging.getLogger(__name__)

ForIndex = namedtuple("ForIndex", ["variable", "range"])


class ForStatement(Statement):
    __slots__ = []

    @property
    def index(self):
        return ForIndex(
            variable=Variable(value_type=ScalarType(), name=self.ast.index),
            range=Expression.compile(self.ast.range, self.context),
        )

    @property
    def body(self):
        return Block(
            ast=self.ast.body,
            context=self.context.create_inner().with_index_variable(self.index),
        )

    @property
    def declared_variables(self):
        return tuple(
            VariableDeclaration(name=var.name, dimensions=var.dimensions, to_allocate=var.to_allocate - 1)
            for stmt in self.body.statements
            for var in stmt.declared_variables
            if var.to_allocate >= 0
        )

    @property
    def variables_to_allocate(self):
        return tuple(
            VariableAllocation(
                name=var.name,
                size=self.index.range.variable_name,
                dimensions=var.dimensions - var.to_allocate,
                indexes=tuple(
                    idx.variable.name
                    for idx in self.context.index_variables[1 - var.to_allocate:]
                ) if var.to_allocate > 1 else ()
            )
            for stmt in self.body.statements
            for var in stmt.declared_variables
            if var.to_allocate > 0
        )

    @property
    def variables(self):
        return tuple(
            Variable(name=var.name, value_type=Variable.value_type_dimensions(var.dimensions))
            for var in self.variables_to_declare
        )

    def validate(self):
        yield from self.body.validate()

    def generate_instructions(self, bindings):
        if self.may_process_requests:
            yield from self.do_generate_instruction(bindings)
        else:
            yield SimpleForInstruction(statement=self, context=bindings)

    def do_generate_instruction(self, bindings):
        size = self.index.range.evaluate(bindings)
        for i in range(size):
            inner_bindings = {
                **bindings,
                self.index.variable.name: [i],
            }
            yield from self.body.generate_instructions(inner_bindings)

    @property
    def context_after(self):
        return self.body.context_after.with_variables(self.variables)

    @property
    def may_process_requests(self):
        return self.body.may_process_requests

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

    def has_downward(self):
        return any(i.has_downward() for i in self.statement.do_generate_instruction(self.context))

    def has_upward(self):
        return any(i.has_upward() for i in self.statement.do_generate_instruction(self.context))

    def on_communicate_downward(self, lines):
        for instruction in self.statement.do_generate_instruction(self.context):
            instruction.on_communicate_downward(lines)

    def on_communicate_upward(self, lines):
        for instruction in self.statement.do_generate_instruction(self.context):
            instruction.on_communicate_downward(lines)
