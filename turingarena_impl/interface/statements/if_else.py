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

    def generate_instructions(self, bindings):
        # FIXME: check that the condition is not yet resolved
        if self.condition.is_assignable():
            # FIXME: use a stricter logic here
            if self.then_body.is_possible_branch(bindings):
                self.condition.assign(bindings, 1)
            else:
                self.condition.assign(bindings, 0)

        if self.condition.evaluate(bindings):
            yield from self.then_body.generate_instructions(bindings)
        elif self.else_body is not None:
            yield from self.else_body.generate_instructions(bindings)

    def expects_request(self, request):
        return (
            self.then_body.expects_request(request) or
            self.else_body is not None and self.else_body.expects_request(request)
        )

    def _get_reference_actions(self):
        for r in self.then_body.reference_actions:
            yield r
        if self.else_body is not None:
            for r in self.else_body.reference_actions:
                yield r
