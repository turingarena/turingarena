from turingarena.interface.executable import ImperativeStatement, Instruction
from turingarena.interface.expressions import Expression
from turingarena.interface.type_expressions import ArrayType


class AllocStatement(ImperativeStatement):
    __slots__ = []

    @property
    def size(self):
        return Expression.compile(self.ast.size)

    @property
    def arguments(self):
        return [Expression.compile(arg) for arg in self.ast.arguments]

    def validate(self):
        assert all(
            isinstance(a.value_type(declared_variables=self.context.variables), ArrayType)
            for a in self.arguments
        )

    def generate_instructions(self, context):
        yield AllocInstruction(arguments=self.arguments, size=self.size, context=context)

    def check_variables(self, initialized_variables, allocated_variables):
        self.size.check_variables(initialized_variables, allocated_variables)

    def allocated_variables(self):
        return [
            exp.resolve_variable()
            for exp in self.arguments
        ]


class AllocInstruction(Instruction):
    __slots__ = ["arguments", "size", "context"]

    def on_communicate_with_process(self, connection):
        size = self.size.evaluate_in(self.context).get()
        for a in self.arguments:
            a.evaluate_in(self.context).alloc(size)
