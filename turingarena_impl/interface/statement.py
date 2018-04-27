from bidict import bidict

from turingarena_impl.interface.node import AbstractSyntaxNodeWrapper


class Statement(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @staticmethod
    def get_statement_classes():
        from turingarena_impl.interface.alloc import AllocStatement
        from turingarena_impl.interface.calls import CallStatement, ReturnStatement
        from turingarena_impl.interface.control import ForStatement, IfStatement, LoopStatement, ExitStatement
        from turingarena_impl.interface.control import BreakStatement, ContinueStatement, SwitchStatement, CaseStatement
        from turingarena_impl.interface.callables import FunctionStatement, CallbackStatement
        from turingarena_impl.interface.mainblocks import InitStatement, MainStatement
        from turingarena_impl.interface.variables import VarStatement
        from turingarena_impl.interface.io import CheckpointStatement, ReadStatement, WriteStatement, FlushStatement

        return bidict({
            "var": VarStatement,
            "function": FunctionStatement,
            "callback": CallbackStatement,
            "init": InitStatement,
            "main": MainStatement,
            "alloc": AllocStatement,
            "checkpoint": CheckpointStatement,
            "read": ReadStatement,
            "write": WriteStatement,
            "flush": FlushStatement,
            "call": CallStatement,
            "return": ReturnStatement,
            "exit": ExitStatement,
            "for": ForStatement,
            "if": IfStatement,
            "loop": LoopStatement,
            "continue": ContinueStatement,
            "break": BreakStatement,
            "switch": SwitchStatement,
            "case": CaseStatement,
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


class SyntheticStatement:
    __slots__ = ["statement_type", "__dict__"]

    def __init__(self, statement_type, **kwargs):
        self.statement_type = statement_type
        self.__dict__ = kwargs
