from turingarena.interface.executable import ImperativeStatement, Instruction
from turingarena.interface.expressions import compile_expression
from turingarena.interface.type_expressions import ArrayType
from turingarena.interface.exceptions import Diagnostic


class AllocStatement(ImperativeStatement):
    __slots__ = []

    @property
    def size(self):
        return compile_expression(self.ast.size, self.context)

    @property
    def arguments(self):
        return tuple(compile_expression(arg, self.context) for arg in self.ast.arguments)

    def validate(self):
        yield from self.size.validate()
        for arg in self.arguments:
            if not isinstance(arg.variable.value_type, ArrayType):
                yield Diagnostic.create_message(f"Argument {arg} is not an array type")
            else:
                for index in arg.indices:
                    yield from index.validate()

    @property
    def context_after(self):
        return self.context.with_allocated_variables({
            arg.variable
            for arg in self.arguments
        })

    def generate_instructions(self, context):
        yield AllocInstruction(arguments=self.arguments, size=self.size, context=context)


class AllocInstruction(Instruction):
    __slots__ = ["arguments", "size", "context"]

    def on_communicate_with_process(self, connection):
        size = self.size.evaluate_in(self.context).get()
        for a in self.arguments:
            a.evaluate_in(self.context).alloc(size)
