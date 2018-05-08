import logging

from turingarena_impl.interface.block import Block
from turingarena_impl.interface.expressions import Expression
from turingarena_impl.interface.statements.statement import Statement

logger = logging.getLogger(__name__)


class IfStatement(Statement):
    __slots__ = []

    @property
    def condition(self):
        return Expression.compile(self.ast.condition, self.context)

    @property
    def then_body(self):
        return Block(ast=self.ast.then_body, context=self.context)

    @property
    def else_body(self):
        return Block(ast=self.ast.else_body, context=self.context) if self.ast.else_body else None

    def validate(self):
        yield from self.condition.validate()
        yield from self.then_body.validate()
        if self.else_body:
            yield from self.else_body.validate()

    def generate_instructions(self, context):
        condition = self.condition.evaluate_in(context)
        if not condition.is_resolved():
            # FIXME: use a stricter logic here
            if self.then_body.is_possible_branch(context):
                condition.resolve(1)
            else:
                condition.resolve(0)

        if condition.get():
            yield from self.then_body.generate_instructions(context)
        elif self.else_body is not None:
            yield from self.else_body.generate_instructions(context)

    def expects_request(self, request):
        return (
            self.then_body.expects_request(request) or
            self.else_body is not None and self.else_body.expects_request(request)
        )

    @property
    def context_after(self):
        initialized_variables = {
            var
            for var in self.then_body.context_after.initialized_variables
            if not self.else_body or var in self.else_body.context_after.initialized_variables
        }
        allocated_variable = {
            var
            for var in self.then_body.context_after.allocated_variables
            if not self.else_body or var in self.else_body.context_after.allocated_variables
        }
        has_flush = self.then_body.context_after.has_flushed_output and (not self.else_body or self.else_body.context_after.has_flushed_output)
        return self.context.with_initialized_variables(initialized_variables)\
            .with_allocated_variables(allocated_variable).with_flushed_output(has_flush)