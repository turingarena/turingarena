from collections import namedtuple

from turingarena.interface.exceptions import Diagnostic
from turingarena.interface.executable import ImperativeStatement, Instruction
from turingarena.interface.expressions import Expression, ReferenceExpression
from turingarena.interface.type_expressions import ArrayType


class AllocStatement(ImperativeStatement):
    __slots__ = []

    @property
    def size(self):
        return Expression.compile(self.ast.size, self.context)

    @property
    def arguments(self):
        return tuple(Expression.compile(arg, self.context) for arg in self.ast.arguments)

    def validate(self):
        yield from self.size.validate()
        for arg in self.arguments:
            if not isinstance(arg, ReferenceExpression) or not arg.variable or not isinstance(arg.variable.value_type, ArrayType):
                yield Diagnostic.create_message(Diagnostic.Messages.NOT_ARRAY_TYPE, arg, parseinfo=self.ast.parseinfo)
            else:
                for index in arg.indices:
                    yield from index.validate()

    @property
    def context_after(self):
        return self.context.with_allocated_variables({
            (arg.variable, self.size.canonical_form)
            for arg in self.arguments
        })

    def generate_instructions(self, context):
        yield AllocInstruction(arguments=self.arguments, size=self.size, context=context)


class AllocInstruction(Instruction, namedtuple("AllocInstruction", [
    "arguments", "size", "context"
])):
    __slots__ = []

    def on_communicate_with_process(self, connection):
        size = self.size.evaluate_in(self.context).get()
        for a in self.arguments:
            a.evaluate_in(self.context).alloc(size)
