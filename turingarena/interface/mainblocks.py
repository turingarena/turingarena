from turingarena.interface.body import Body
from turingarena.interface.context import StaticContext
from turingarena.interface.exceptions import GlobalVariableNotInitializedError
from turingarena.interface.statement import Statement


class EntryPointStatement(Statement):
    __slots__ = []

    @property
    def body(self):
        return Body(self.ast.body)

    def contextualized_body(self, context):
        return self.body, StaticContext(
            callbacks=context.callbacks,
            functions=context.functions,
            global_variables=context.global_variables,
            variables=context.global_variables,
        )

    def validate(self, context):
        self.body.validate(context)


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
