from turingarena_impl.interface.block import ImperativeBlock
from turingarena_impl.interface.statement import Statement


class MainStatement(Statement):
    __slots__ = []

    @property
    def body(self):
        return ImperativeBlock(ast=self.ast.body, context=self.context.create_local())

    def validate(self):
        yield from self.body.validate()

    @property
    def context_after(self):
        new_context = self.body.context_after
        return self.context.with_initialized_variables(new_context.initialized_variables)\
            .with_allocated_variables(new_context.allocated_variables)\
            .with_flushed_output(new_context.has_flushed_output)
