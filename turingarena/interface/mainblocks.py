from turingarena.common import ImmutableObject
from turingarena.interface.body import Body
from turingarena.interface.statement import Statement


class Init(ImmutableObject):
    __slots__ = ["body"]

    def check_variables(self, initialized_variables, allocated_variables):
        self.body.check_variables(initialized_variables, allocated_variables)


class InitStatement(Statement):
    __slots__ = ["init"]

    @staticmethod
    def compile(ast, scope):
        init = Init(body=Body.compile(ast.body, scope=scope))
        scope.main["init"] = init
        return InitStatement(init=init)

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
        scope.main["main"] = main
        return MainStatement(main=main)

    def check_variables(self, initialized_variables, allocated_variables):
        self.main.check_variables(initialized_variables, allocated_variables)
