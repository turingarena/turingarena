import logging
from abc import abstractmethod
from collections import OrderedDict

from bidict import bidict

from turingarena.protocol.model.expressions import Expression
from turingarena.protocol.model.node import AbstractSyntaxNode, ImmutableObject, TupleLikeObject
from turingarena.protocol.model.scope import Scope
from turingarena.protocol.model.type_expressions import ValueType, ScalarType, ArrayType

logger = logging.getLogger(__name__)

statement_classes = bidict()


def statement_class(statement_type):
    def decorator(cls):
        statement_classes[statement_type] = cls
        return cls

    return decorator


class Protocol(AbstractSyntaxNode):
    __slots__ = ["package_name", "file_name", "body"]

    @staticmethod
    def compile(*, ast, **kwargs):
        logger.debug("compiling {}".format(ast))
        scope = Scope()
        return Protocol(
            body=Body.compile(ast.body, scope=scope),
            **kwargs,
        )


class Statement(AbstractSyntaxNode):
    __slots__ = ["statement_type"]

    def __init__(self, **kwargs):
        super().__init__(statement_type=statement_classes.inv[self.__class__], **kwargs)

    @staticmethod
    def compile(ast, scope):
        logger.debug("compiling statement {}".format(ast))
        return statement_classes[ast.statement_type].compile(ast, scope)


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
    __slots__ = ["type", "variables"]

    @staticmethod
    def compile(ast, scope):
        value_type = ValueType.compile(ast.type_expression, scope=scope)
        variables = [
            Variable(type=value_type, name=d.name)
            for d in ast.declarators
        ]
        for v in variables:
            scope.variables[v.name] = v
        return VarStatement(
            type=value_type,
            variables=variables
        )


class Body(AbstractSyntaxNode):
    __slots__ = ["statements", "scope"]

    @staticmethod
    def compile(ast, *, scope):
        scope = Scope(scope)
        return Body(
            scope=scope,
            statements=[
                Statement.compile(s, scope=scope)
                for s in ast.statements
            ]
        )


class InterfaceSignature(TupleLikeObject):
    __slots__ = ["variables", "functions", "callbacks"]


class Interface(ImmutableObject):
    __slots__ = ["name", "signature", "body"]

    @staticmethod
    def compile(ast, scope):
        body = Body.compile(ast.body, scope=scope)
        signature = InterfaceSignature(
            variables=OrderedDict(
                body.scope.variables.items()
            ),
            functions=OrderedDict(
                (c.signature.name, c.signature)
                for c in body.scope.functions.values()
            ),
            callbacks=OrderedDict(
                (c.signature.name, c.signature)
                for c in body.scope.callbacks.values()
            ),
        )
        return Interface(
            name=ast.name,
            signature=signature,
            body=body,
        )


@statement_class("interface")
class InterfaceStatement(Statement):
    __slots__ = ["interface"]

    @staticmethod
    def compile(ast, scope):
        interface = Interface.compile(ast, scope)
        scope.interfaces[interface.name] = interface
        return InterfaceStatement(interface=interface)


class CallableSignature(TupleLikeObject):
    __slots__ = ["name", "parameters", "return_type"]

    @staticmethod
    def compile(ast, scope):
        parameters = [
            Variable(
                type=ValueType.compile(p.type_expression, scope=scope),
                name=p.declarator.name,
            )
            for p in ast.parameters
        ]

        return CallableSignature(
            name=ast.name,
            parameters=parameters,
            return_type=ValueType.compile(ast.return_type, scope=scope),
        )


class Callable(ImmutableObject):
    __slots__ = ["signature"]


class Function(Callable):
    __slots__ = []

    @staticmethod
    def compile(ast, scope):
        return Function(signature=CallableSignature.compile(ast.signature, scope))


@statement_class("function")
class FunctionStatement(Statement):
    __slots__ = ["function"]

    @staticmethod
    def compile(ast, scope):
        fun = Function.compile(ast, scope)
        scope.functions[fun.signature.name] = fun
        return FunctionStatement(
            function=fun
        )


class Callback(Callable):
    __slots__ = ["body"]

    @staticmethod
    def compile(ast, scope):
        signature = CallableSignature.compile(ast.signature, scope)
        callback_scope = Scope(scope)
        for p in signature.parameters:
            callback_scope.variables[p.name] = p
        return Callback(
            signature=signature,
            body=Body.compile(ast.body, scope=callback_scope)
        )


@statement_class("callback")
class CallbackStatement(Statement):
    __slots__ = ["callback"]

    @staticmethod
    def compile(ast, scope):
        callback = Callback.compile(ast, scope=scope)
        scope.callbacks[callback.signature.name] = callback
        return CallbackStatement(callback=callback)


class Main(ImmutableObject):
    __slots__ = ["body"]

    def run(self, context):
        yield from run_body(self.body, context)
        yield


@statement_class("main")
class MainStatement(Statement):
    __slots__ = ["main"]

    @staticmethod
    def compile(ast, scope):
        main = Main(body=Body.compile(ast.body, scope=scope))
        scope.main["main"] = main
        return MainStatement(main=main)


class ImperativeStatement(Statement):
    __slots__ = ["first_call"]

    @abstractmethod
    def run_porcelain(self, *, context, frame):
        pass

    @abstractmethod
    def run_plumbing(self, context):
        pass


@statement_class("alloc")
class AllocStatement(ImperativeStatement):
    __slots__ = ["arguments", "size"]

    @staticmethod
    def compile(ast, scope):
        arguments = [Expression.compile(arg, scope=scope) for arg in ast.arguments]
        assert all(isinstance(a.value_type, ArrayType) for a in arguments)
        return AllocStatement(
            arguments=arguments,
            size=Expression.compile(ast.size, scope=scope, expected_type=ScalarType(int)),
        )

    def run_porcelain(self, *, context, frame):
        size = self.size.evaluate(frame=frame).get()
        for a in self.arguments:
            array_reference = a.evaluate(frame=frame)
            array_reference.alloc(frame=frame, size=size)


class InputOutputStatement(ImperativeStatement):
    __slots__ = ["arguments"]

    @classmethod
    def compile(cls, ast, scope):
        return cls(
            arguments=[
                Expression.compile(arg, scope=scope)
                for arg in ast.arguments
            ],
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
        fun = scope.functions[ast.function_name]
        assert len(ast.parameters) == len(fun.signature.parameters)
        return CallStatement(
            function=fun,
            parameters=[
                Expression.compile(arg, scope=scope, expected_type=decl_arg.type)
                for decl_arg, arg in zip(fun.signature.parameters, ast.parameters)
            ],
            return_value=Expression.compile(
                ast.return_value,
                scope=scope,
                expected_type=fun.signature.return_type,
            ),
        )

    def run_porcelain(self, *, context, frame):
        call = context.get_next_call()


@statement_class("return")
class ReturnStatement(ImperativeStatement):
    __slots__ = ["value"]

    @staticmethod
    def compile(ast, scope):
        return ReturnStatement(
            value=Expression.compile(ast.value, scope=scope),
        )


class ForIndex(ImmutableObject):
    __slots__ = ["variable", "range"]


@statement_class("for")
class ForStatement(ImperativeStatement):
    __slots__ = ["index", "body", "scope"]

    @staticmethod
    def compile(ast, scope):
        for_scope = Scope(scope)
        index_var = Variable(type=ScalarType(int), name=ast.index.declarator.name)
        for_scope.variables[index_var.name] = index_var
        return ForStatement(
            index=ForIndex(
                variable=index_var,
                range=Expression.compile(ast.index.range, scope=scope),
            ),
            body=Body.compile(ast.body, scope=for_scope),
            scope=for_scope,
        )


def run_body(body, context):
    for statement in body.statements:
        if isinstance(statement, ImperativeStatement):
            yield from statement.run(context)
