import logging

from turingarena.protocol.analysis.expression import compile_expression
from turingarena.protocol.analysis.scope import Scope
from turingarena.protocol.analysis.type_expression import compile_type_expression
from turingarena.protocol.model.node import AbstractSyntaxNode, ImmutableObject
from turingarena.protocol.types import scalar

logger = logging.getLogger(__name__)

statement_classes = {}
statement_types = {}


def statement_class(statement_type):
    def decorator(cls):
        statement_classes[statement_type] = cls
        statement_types[cls] = statement_type
        return cls

    return decorator


class Protocol(AbstractSyntaxNode):
    __slots__ = ["body"]

    @staticmethod
    def compile(ast):
        logger.debug("compiling {}".format(ast))
        scope = Scope()
        return Protocol(
            body=Body.compile(ast.body, scope=scope)
        )


class Statement(AbstractSyntaxNode):
    __slots__ = ["statement_type"]

    def __init__(self, **kwargs):
        super().__init__(statement_type=statement_types[self.__class__], **kwargs)


class VarDeclarator(AbstractSyntaxNode):
    __slots__ = ["name"]

    @staticmethod
    def compile(ast, scope):
        declarator = VarDeclarator(name=ast.name)
        scope["var", ast.name] = declarator
        return declarator


class Variable(ImmutableObject):
    __slots__ = ["type", "name"]


@statement_class("var")
class VarStatement(Statement):
    __slots__ = ["type", "vars"]

    @staticmethod
    def compile(ast, scope):
        compile_type_expression(ast.type_expression)
        variables = [
            Variable(type=ast.type_expression.descriptor, name=d.name)
            for d in ast.declarators
        ]
        for v in variables:
            scope["var", v.name] = v
        return VarStatement(
            type=ast.type_expression.descriptor,
            vars=variables
        )


class Body(AbstractSyntaxNode):
    __slots__ = ["statements", "scope"]

    @staticmethod
    def compile(ast, *, scope):
        scope = Scope(scope)
        return Body(
            scope=scope,
            statements=[
                compile_statement(s, scope=scope)
                for s in ast.statements
            ]
        )


@statement_class("interface")
class InterfaceStatement(Statement):
    __slots__ = ["name", "body"]

    @staticmethod
    def compile(ast, scope):
        return InterfaceStatement(
            name=ast.name,
            body=Body.compile(ast.body, scope=scope)
        )


class CallableDeclarator(AbstractSyntaxNode):
    __slots__ = ["name", "parameters", "return_type", "scope"]

    @staticmethod
    def compile(ast, scope):
        scope = Scope(scope)
        for parameter in ast.parameters:
            compile_type_expression(parameter.type_expression)
        parameters = [
            Variable(type=p.type_expression.descriptor, name=p.declarator.name)
            for p in ast.parameters
        ]
        for p in parameters:
            scope["var", p.name] = p

        return CallableDeclarator(
            name=ast.name,
            parameters=parameters,
            return_type=ast.return_type,
            scope=scope
        )


class Callable(ImmutableObject):
    __slots__ = ["declarator"]


class Function(Callable):
    __slots__ = []

    @staticmethod
    def compile(ast, scope):
        return Function(declarator=CallableDeclarator.compile(ast.declarator, scope))


@statement_class("function")
class FunctionStatement(Statement):
    __slots__ = ["function"]

    @staticmethod
    def compile(ast, scope):
        fun = Function.compile(ast, scope)
        scope["function", fun.declarator.name] = fun
        return FunctionStatement(
            function=fun
        )


class Callback(Callable):
    __slots__ = ["body"]

    @staticmethod
    def compile(ast, scope):
        declarator = CallableDeclarator.compile(ast.declarator, scope)
        return Callback(
            declarator=declarator,
            body=Body.compile(ast.body, scope=declarator.scope)
        )


@statement_class("callback")
class CallbackStatement(Statement):
    __slots__ = ["callback"]

    @staticmethod
    def compile(ast, scope):
        callback = Callback.compile(ast, scope=scope)
        scope["callback", callback.declarator.name] = callback
        return CallbackStatement(callback=callback)


class Main(ImmutableObject):
    __slots__ = ["body"]


@statement_class("main")
class MainStatement(Statement):
    __slots__ = ["main"]

    @staticmethod
    def compile(ast, scope):
        main = Main(body=Body.compile(ast.body, scope=scope))
        scope["main", "main"] = main
        return MainStatement(main=main)


class ImperativeStatement(Statement):
    __slots__ = ["first_call"]


@statement_class("alloc")
class AllocStatement(ImperativeStatement):
    __slots__ = ["arguments", "size"]

    @staticmethod
    def compile(ast, scope):
        for arg in ast.arguments:
            compile_expression(arg, scope=scope)
        compile_expression(ast.size, scope=scope)
        return AllocStatement(
            arguments=ast.arguments,
            size=ast.size,
        )


class InputOutputStatement(ImperativeStatement):
    __slots__ = ["arguments"]

    @classmethod
    def compile(cls, ast, scope):
        for arg in ast.arguments:
            compile_expression(arg, scope=scope)
        return cls(
            arguments=ast.arguments,
        )


@statement_class("input")
class InputStatement(InputOutputStatement):
    __slots__ = []


@statement_class("output")
class OutputStatement(InputOutputStatement):
    __slots__ = []


@statement_class("flush")
class FlushStatement(ImperativeStatement):
    __slots__ = []

    @staticmethod
    def compile(ast, scope):
        return FlushStatement()


@statement_class("call")
class CallStatement(ImperativeStatement):
    __slots__ = ["function", "parameters", "return_value"]

    @staticmethod
    def compile(ast, scope):
        fun = scope["function", ast.function_name]
        assert len(ast.parameters) == len(fun.declarator.parameters)
        for decl_arg, arg in zip(fun.declarator.parameters, ast.parameters):
            compile_expression(arg, scope=scope)
            assert arg.type == decl_arg.type
        compile_expression(ast.return_value, scope=scope)
        return CallStatement(
            function=fun,
            parameters=ast.parameters,
            return_value=ast.return_value,
        )


@statement_class("return")
class ReturnStatement(ImperativeStatement):
    __slots__ = ["value"]

    @staticmethod
    def compile(ast, scope):
        compile_expression(ast.value, scope=scope)
        return ReturnStatement(
            value=ast.value,
        )


class ForIndex(ImmutableObject):
    __slots__ = ["variable", "range"]


@statement_class("for")
class ForStatement(ImperativeStatement):
    __slots__ = ["index", "body", "scope"]

    @staticmethod
    def compile(ast, scope):
        compile_expression(ast.index.range, scope=scope)
        scope = Scope(scope)
        index_var = Variable(type=scalar(int), name=ast.index.declarator.name)
        scope["var", index_var.name] = index_var
        return ForStatement(
            index=ForIndex(variable=index_var, range=ast.index.range),
            body=Body.compile(ast.body, scope=scope),
            scope=scope,
        )


def compile_statement(ast, *, scope):
    logger.debug("compiling statement {}".format(ast))
    return statement_classes[ast.statement_type].compile(ast, scope)
