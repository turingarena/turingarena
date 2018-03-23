from turingarena.common import ImmutableObject
from turingarena.interface.body import Body
from turingarena.interface.exceptions import GlobalVariableNotInitializedError
from turingarena.interface.statement import Statement


class Init(ImmutableObject):
    __slots__ = ["body"]

    def check_variables(self, initialized_variables, allocated_variables):
        self.body.check_variables(initialized_variables, allocated_variables)

        for var in list(self.body.scope.variables.values()):
            if var not in initialized_variables:
                raise GlobalVariableNotInitializedError(f"Global variable '{var.name}' not initialized in 'init' block")


class InitStatement(Statement):
    __slots__ = ["init"]

    @staticmethod
    def compile(ast, scope):
        init = Init(body=Body.compile(ast.body, scope=scope))
        return InitStatement(ast=ast, init=init)

    def check_variables(self, initialized_variables, allocated_variables):
        self.init.check_variables(initialized_variables, allocated_variables)


class Main(ImmutableObject):
    __slots__ = ["body"]

    def check_variables(self, initialized_variables, allocated_variables):
        self.body.check_variables(initialized_variables, allocated_variables)


class MainStatement(Statement):
    __slots__ = ["main"]

    @staticmethod
    def compile(ast, scope):
        main = Main(body=Body.compile(ast.body, scope=scope))
        return MainStatement(ast=ast, main=main)

    def check_variables(self, initialized_variables, allocated_variables):
        self.main.check_variables(initialized_variables, allocated_variables)
