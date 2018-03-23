from turingarena.interface.executable import ImperativeStatement, Instruction
from turingarena.interface.expressions import Expression
from turingarena.interface.type_expressions import ArrayType


class AllocStatement(ImperativeStatement):
    __slots__ = ["arguments", "size"]

    @staticmethod
    def compile(ast, scope):
        arguments = [Expression.compile(arg) for arg in ast.arguments]
        assert all(isinstance(a.value_type(declared_variables=scope.variables), ArrayType) for a in arguments)
        return AllocStatement(
            ast=ast,
            arguments=arguments,
            size=Expression.compile(ast.size),
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
