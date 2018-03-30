from turingarena.interface.exceptions import Diagnostic
from turingarena.interface.statement import Statement
from turingarena.interface.block import ImperativeBlock


class EntryPointStatement(Statement):
    __slots__ = []

    @property
    def body(self):
        return ImperativeBlock(ast=self.ast.body, context=self.context.create_local())

    def validate(self):
        yield from self.body.validate()

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

    def validate(self):
        yield from self.body.validate()

        new_context = self.context_after
        for var in self.context.global_variables:
            if var not in new_context.initialized_variables:
                yield Diagnostic(f"global variable {var.name} not initialized in init block", parseinfo=self.ast.parseinfo)


class MainStatement(EntryPointStatement):
    __slots__ = []

