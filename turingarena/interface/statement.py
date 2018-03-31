from bidict import bidict

from turingarena.interface.node import AbstractSyntaxNodeWrapper


class Statement(AbstractSyntaxNodeWrapper):
    __slots__ = []

    @staticmethod
    def get_statement_classes():
        from turingarena.interface.alloc import AllocStatement
        from turingarena.interface.calls import CallStatement, ReturnStatement
        from turingarena.interface.control import ForStatement, IfStatement, LoopStatement, ExitStatement
        from turingarena.interface.callables import FunctionStatement, CallbackStatement
        from turingarena.interface.mainblocks import InitStatement, MainStatement
        from turingarena.interface.variables import VarStatement
        from turingarena.interface.io import CheckpointStatement, InputStatement, OutputStatement, FlushStatement

        return bidict({
            "var": VarStatement,
            "function": FunctionStatement,
            "callback": CallbackStatement,
            "init": InitStatement,
            "main": MainStatement,
            "alloc": AllocStatement,
            "checkpoint": CheckpointStatement,
            "input": InputStatement,
            "output": OutputStatement,
            "flush": FlushStatement,
            "call": CallStatement,
            "return": ReturnStatement,
            "exit": ExitStatement,
            "for": ForStatement,
            "if": IfStatement,
            "loop": LoopStatement,
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
