from turingarena.interface.executable import ImperativeStatement, Instruction
from turingarena.interface.expressions import Expression
from turingarena.interface.type_expressions import ArrayType, ScalarType


class AllocStatement(ImperativeStatement):
    __slots__ = ["arguments", "size"]

    @staticmethod
    def compile(ast, scope):
        arguments = [Expression.compile(arg, scope=scope) for arg in ast.arguments]
        assert all(isinstance(a.value_type, ArrayType) for a in arguments)
        return AllocStatement(
            arguments=arguments,
            size=Expression.compile(ast.size, scope=scope, expected_type=ScalarType(int)),
        )

    def generate_instructions(self, frame):
        yield AllocInstruction(arguments=self.arguments, size=self.size, frame=frame)


class AllocInstruction(Instruction):
    __slots__ = ["arguments", "size", "frame"]

    def on_communicate_with_process(self, connection):
        size = self.size.evaluate_in(self.frame).get()
        for a in self.arguments:
            a.evaluate_in(self.frame).alloc(size)
