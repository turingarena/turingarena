from bidict import bidict

from turingarena_impl.interface.common import ImperativeStructure


class Statement(ImperativeStructure):
    __slots__ = []

    @staticmethod
    def get_statement_classes():
        from turingarena_impl.interface.statements.call_statement import CallStatement, ReturnStatement
        from turingarena_impl.interface.statements.loop_statement import LoopStatement
        from turingarena_impl.interface.statements.for_statement import ForStatement
        from turingarena_impl.interface.statements.if_statement import IfStatement
        from turingarena_impl.interface.statements.exit_statement import ExitStatement
        from turingarena_impl.interface.statements.switch_statement import SwitchStatement
        from turingarena_impl.interface.statements.loop_statement import BreakStatement
        from turingarena_impl.interface.statements.io_statements import CheckpointStatement, ReadStatement, WriteStatement
        from turingarena_impl.interface.callables import CallbackStatement

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
            "callback": CallbackStatement,
        })

    @staticmethod
    def compile(ast, context):
        return Statement.get_statement_classes()[ast.statement_type](ast=ast, context=context)

    @property
    def statement_type(self):
        return self.get_statement_classes().inv[self.__class__]

    @property
    def context_after(self):
        return self.context

    def validate(self):
        return []

    def expects_request(self, request):
        if request is None:
            return True
        return False

    @property
    def variables_to_declare(self):
        return tuple(
            var
            for var in self.declared_variables
            if var.to_allocate == 0
        )

    @property
    def declared_variables(self):
        return ()

    @property
    def variables_to_allocate(self):
        return ()


class SyntheticStatement:
    __slots__ = ["statement_type", "__dict__"]

    def __init__(self, statement_type, **kwargs):
        self.statement_type = statement_type
        self.__dict__ = kwargs
