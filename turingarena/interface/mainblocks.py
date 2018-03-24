from turingarena.interface.block import ImperativeBlock
from turingarena.interface.exceptions import GlobalVariableNotInitializedError
from turingarena.interface.statement import Statement


class EntryPointStatement(Statement):
    __slots__ = []

    @property
    def body(self):
        return ImperativeBlock(ast=self.ast.body, context=self.context.create_local())

    def validate(self):
        self.body.validate()


class InitStatement(EntryPointStatement):
    __slots__ = []

    def check_variables(self, initialized_variables, allocated_variables):
        self.body.check_variables(initialized_variables, allocated_variables)

        for var in self.body.declared_variables().values():
            if var not in initialized_variables:
                raise GlobalVariableNotInitializedError(f"Global variable '{var.name}' not initialized in 'init' block")


class MainStatement(EntryPointStatement):
    __slots__ = []

    def check_variables(self, initialized_variables, allocated_variables):
        self.check_variables(initialized_variables, allocated_variables)
