from turingarena.interface.executable import SimpleStatement
from turingarena.interface.expressions import Expression
from turingarena.interface.type_expressions import ArrayType, ScalarType


class AllocStatement(SimpleStatement):
    __slots__ = ["arguments", "size"]

    @staticmethod
    def compile(ast, scope):
        arguments = [Expression.compile(arg, scope=scope) for arg in ast.arguments]
        assert all(isinstance(a.value_type, ArrayType) for a in arguments)
        return AllocStatement(
            arguments=arguments,
            size=Expression.compile(ast.size, scope=scope, expected_type=ScalarType(int)),
        )

    def run_sandbox(self, connection, *, frame):
        self.do_alloc(frame)

    def run_driver_pre(self, request, *, frame):
        self.do_alloc(frame)

    def do_alloc(self, frame):
        size = self.size.evaluate_in(frame).get()
        for a in self.arguments:
            a.evaluate_in(frame).alloc(size)
