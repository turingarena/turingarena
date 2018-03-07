from bidict import bidict


def compile_statement(ast, *, scope):
    return get_statement_classes()[ast.statement_type].compile(ast, scope)


def get_statement_classes():
    from turingarena.interface.alloc import AllocStatement
    from turingarena.interface.calls import CallStatement, ReturnStatement
    from turingarena.interface.control import ForStatement, IfStatement, LoopStatement, ExitStatement
    from turingarena.interface.callables import FunctionStatement, CallbackStatement, MainStatement
    from turingarena.interface.variables import VarStatement
    from turingarena.interface.io import CheckpointStatement, InputStatement, OutputStatement, FlushStatement

    return bidict({
        "var": VarStatement,
        "function": FunctionStatement,
        "callback": CallbackStatement,
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
