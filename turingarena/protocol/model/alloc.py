from turingarena.protocol.driver.frames import Phase
from turingarena.protocol.model.expressions import Expression
from turingarena.protocol.model.statement import ImperativeStatement
from turingarena.protocol.model.type_expressions import ArrayType, ScalarType


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

    def run(self, context):
        if context.phase is Phase.RUN:
            size = context.evaluate(self.size).get()
            for a in self.arguments:
                context.evaluate(a).alloc(size=size)
        yield from []
