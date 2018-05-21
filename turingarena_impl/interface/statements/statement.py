from bidict import bidict

from turingarena_impl.interface.common import ImperativeStructure, AbstractSyntaxNodeWrapper
from turingarena_impl.interface.variables import ReferenceActionType


class AbstractStatement(ImperativeStructure):
    __slots__ = []

    def validate(self):
        return []

    def expects_request(self, request):
        if request is None:
            return True
        return False

    @property
    def needs_flush(self):
        return False

    def generate_instructions(self, bindings):
        raise NotImplementedError

    @property
    def variables_to_declare(self):
        return list(self._get_variables_to_declare())

    def _get_variables_to_declare(self):
        for inst in self.instructions:
            for a in inst.reference_actions:
                if a.reference.index_count == 0 and a.action_type == ReferenceActionType.DECLARED:
                    yield a.reference.variable

    @property
    def variables_to_allocate(self):
        return list(self._get_allocations())

    def _get_allocations(self):
        return []


class Statement(AbstractStatement, AbstractSyntaxNodeWrapper):
    __slots__ = []

    @staticmethod
    def get_statement_classes():
        from .call import CallStatement, ReturnStatement
        from .loop import LoopStatement, BreakStatement
        from .for_loop import ForStatement
        from .if_else import IfStatement
        from .exit import ExitStatement
        from .switch import SwitchStatement
        from .io import CheckpointStatement, ReadStatement, WriteStatement

        return bidict({
            "checkpoint": CheckpointStatement,
            "read": ReadStatement,
            "write": WriteStatement,
            "call": CallStatement,
            "return": ReturnStatement,
            "exit": ExitStatement,
            "for": ForStatement,
            "if": IfStatement,
            "loop": LoopStatement,
            "break": BreakStatement,
            "switch": SwitchStatement,
        })

    @staticmethod
    def compile(ast, context):
        return Statement.get_statement_classes()[ast.statement_type](ast=ast, context=context)

    @property
    def statement_type(self):
        return self.ast.statement_type


class SyntheticStatement(AbstractStatement):
    __slots__ = ["statement_type", "__dict__"]

    def __init__(self, statement_type, **kwargs):
        self.statement_type = statement_type
        self.__dict__ = kwargs
