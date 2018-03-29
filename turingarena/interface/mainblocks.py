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

    @property
    def context_after(self):
        return self.context.with_initialized_variables({
            variable
            for variable in self.body.context_after.initialized_variables
            if variable not in self.context.initialized_variables
        }).with_allocated_variables({
            variable
            for variable in self.body.context_after.allocated_variables
            if variable not in self.context.allocated_variables
        })


class InitStatement(EntryPointStatement):
    __slots__ = []


class MainStatement(EntryPointStatement):
    __slots__ = []

