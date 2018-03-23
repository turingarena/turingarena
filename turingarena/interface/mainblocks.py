from turingarena.common import ImmutableObject
from turingarena.interface.body import Body
from turingarena.interface.exceptions import GlobalVariableNotInitializedError
from turingarena.interface.statement import Statement


class Init(ImmutableObject):
    __slots__ = ["body"]

    def check_variables(self, initialized_variables, allocated_variables):
        self.body.check_variables(initialized_variables, allocated_variables)

        for var in self.body.declared_variables().values():
            if var not in initialized_variables:
                raise GlobalVariableNotInitializedError(f"Global variable '{var.name}' not initialized in 'init' block")


class InitStatement(Statement):
    __slots__ = []

    @property
    def init(self):
        return Init(body=Body.compile(self.ast.body))

    def validate(self, context):
        self.init.body.validate(context)

    def check_variables(self, initialized_variables, allocated_variables):
        self.init.check_variables(initialized_variables, allocated_variables)


class Main(ImmutableObject):
    __slots__ = ["body"]

    def check_variables(self, initialized_variables, allocated_variables):
        self.body.check_variables(initialized_variables, allocated_variables)


class MainStatement(Statement):
    __slots__ = []

    @property
    def main(self):
        return Main(body=Body.compile(self.ast.body))

    def validate(self, context):
        self.main.body.validate(context)

    def check_variables(self, initialized_variables, allocated_variables):
        self.main.check_variables(initialized_variables, allocated_variables)
