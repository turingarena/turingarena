import logging

from turingarena_impl.interface.common import ImperativeStructure, AbstractSyntaxNodeWrapper, Step
from turingarena_impl.interface.diagnostics import Diagnostic
from turingarena_impl.interface.expressions import SyntheticExpression
from turingarena_impl.interface.statements.statement import Statement, SyntheticStatement
from turingarena_impl.interface.variables import ReferenceActionType

logger = logging.getLogger(__name__)


class Block(ImperativeStructure, AbstractSyntaxNodeWrapper):
    __slots__ = []

    def _generate_statements(self):
        inner_context = self.context
        for s in self.ast.statements:
            statement = Statement.compile(s, inner_context)

            for inst in statement.instructions:
                inner_context = inner_context.with_reference_actions(inst.reference_actions)

            yield statement

    @property
    def statements(self):
        return list(self._generate_statements())

    def validate(self):
        from turingarena_impl.interface.statements.loop import BreakStatement
        from turingarena_impl.interface.statements.exit import ExitStatement

        for i, statement in enumerate(self.statements):
            yield from statement.validate()
            if isinstance(statement, BreakStatement) or isinstance(statement, ExitStatement):
                if i < len(self.statements) - 1:
                    yield Diagnostic(Diagnostic.Messages.UNREACHABLE_CODE, parseinfo=self.ast.parseinfo)
                    break

    @property
    def synthetic_statements(self):
        for s in self.statements:
            yield s
            if s.statement_type == "call" and s.method.has_callbacks:
                yield SyntheticStatement("write", arguments=[
                    SyntheticExpression("int_literal", value=0),  # no more callbacks
                ])

    def collect_step_instructions(self, instructions):
        unresolved_references = set()
        for inst in instructions:
            yield inst
            for a in inst.reference_actions:
                if a.action_type is ReferenceActionType.DECLARED:
                    unresolved_references.add(a.reference)
                if a.action_type is ReferenceActionType.RESOLVED:
                    assert a.reference in unresolved_references
                    unresolved_references.remove(a.reference)
            logger.debug(f"Inst: {type(inst).__name__}. unresolved_references: {unresolved_references}")
            if not unresolved_references:
                return

    def _generate_instructions(self):
        for s in self.statements:
            yield from s.instructions

    @property
    def steps(self):
        return list(self._generate_steps())

    def _generate_steps(self):
        instructions = self._generate_instructions()
        while True:
            step_instructions = list(self.collect_step_instructions(instructions))
            if not step_instructions:
                break
            yield Step(step_instructions)

    @property
    def reference_actions(self):
        return [
            a
            for step in self.steps
            for inst in step.instructions
            for a in inst.reference_actions
        ]

    def expects_request(self, request):
        for s in self.statements:
            if s.expects_request(request):
                return True
            if not s.expects_request(None):
                break

    @property
    def may_process_requests(self):
        return any(
            s.may_process_requests
            for s in self.statements
        )
