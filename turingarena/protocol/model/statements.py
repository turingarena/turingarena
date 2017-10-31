import logging

from bidict import bidict

from turingarena.protocol.model.expressions import Expression
from turingarena.protocol.model.node import AbstractSyntaxNode, ImmutableObject, TupleLikeObject
from turingarena.protocol.model.scope import Scope
from turingarena.protocol.model.type_expressions import ValueType, ScalarType, ArrayType
from turingarena.protocol.server.commands import FunctionReturn

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
            variables=list(body.scope.variables.values()),
            functions={
                c.name: c.signature
                for c in body.scope.functions.values()
            },
            callbacks={
                c.name: c.signature
                for c in body.scope.callbacks.values()
            },
        )
        return Interface(
            name=ast.name,
            signature=signature,
            body=body,
        )

    def preflight(self, context):
        with context.new_frame(parent=None, scope=self.body.scope) as frame:
            request = context.peek_request()
            assert request.message_type == "main_begin"
            for variable, value in request.global_variables:
                frame[variable] = value
            context.complete_request()

            main = self.body.scope.main["main"]
            main.preflight(context=context, frame=frame)

            request = context.peek_request()
            assert request.message_type == "main_end"
            context.complete_request()

    def run(self, context):
        main = self.body.scope.main["main"]
        yield from run_body(main.body, context=context, frame=context.root_frame)
        yield


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
    __slots__ = ["name", "signature"]


class Function(Callable):
    __slots__ = []

    @staticmethod
    def compile(ast, scope):
        return Function(
            name=ast.declarator.name,
            signature=CallableSignature.compile(ast.declarator, scope),
        )


@statement_class("function")
class FunctionStatement(Statement):
    __slots__ = ["function"]

    @staticmethod
    def compile(ast, scope):
        fun = Function.compile(ast, scope)
        scope.functions[fun.name] = fun
        return FunctionStatement(
            function=fun
        )


class Callback(Callable):
    __slots__ = ["scope", "body"]

    @staticmethod
    def compile(ast, scope):
        signature = CallableSignature.compile(ast.declarator, scope)
        callback_scope = Scope(scope)
        for p in signature.parameters:
            callback_scope.variables[p.name] = p
        return Callback(
            name=ast.declarator.name,
            signature=signature,
            scope=callback_scope,
            body=Body.compile(ast.body, scope=callback_scope)
        )

    def preflight(self, *, context):
        with context.new_frame(scope=self.scope, parent=context.root_frame) as new_frame:
            preflight_body(self.body, context=context, frame=new_frame)

    def run(self, *, context):
        logger.debug(f"running callback {self}")
        with context.new_frame(scope=self.scope, parent=context.root_frame) as new_frame:
            yield from run_body(self.body, context=context, frame=new_frame)


@statement_class("callback")
class CallbackStatement(Statement):
    __slots__ = ["callback"]

    @staticmethod
    def compile(ast, scope):
        callback = Callback.compile(ast, scope=scope)
        scope.callbacks[callback.name] = callback
        return CallbackStatement(callback=callback)


class Main(ImmutableObject):
    __slots__ = ["body"]

    def preflight(self, *, context, frame):
        preflight_body(self.body, context=context, frame=frame)

    def run(self, *, context, frame):
        yield from run_body(self.body, context=context, frame=frame)


@statement_class("main")
class MainStatement(Statement):
    __slots__ = ["main"]

    @staticmethod
    def compile(ast, scope):
        main = Main(body=Body.compile(ast.body, scope=scope))
        scope.main["main"] = main
        return MainStatement(main=main)


class ImperativeStatement(Statement):
    # TODO: first_call
    __slots__ = []

    def preflight(self, *, context, frame):
        pass

    def run(self, *, context, frame):
        yield from []


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

    def run(self, *, context, frame):
        size = self.size.evaluate(frame=frame).get()
        for a in self.arguments:
            array_reference = a.evaluate(frame=frame)
            array_reference.alloc(size=size)
        yield from []


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

    def run(self, *, context, frame):
        raw_values = [
            a.value_type.format(a.evaluate(frame=frame).get())
            for a in self.arguments
        ]
        logger.debug(f"printing {raw_values} to downward_pipe")
        # FIXME: should flush only once per communication block
        print(*raw_values, file=context.process_connection.downward_pipe, flush=True)
        yield from []


@statement_class("output")
class OutputStatement(InputOutputStatement):
    __slots__ = []

    def run(self, *, context, frame):
        logger.debug(f"reading from upward_pipe...")
        line = context.process_connection.upward_pipe.readline()
        raw_values = line.strip().split()
        logger.debug(f"read {raw_values} from upward_pipe")
        for a, v in zip(self.arguments, raw_values):
            value = a.value_type.parse(v)
            a.evaluate(frame=frame).resolve(value)
        yield from []


@statement_class("flush")
class FlushStatement(ImperativeStatement):
    __slots__ = []

    @staticmethod
    def compile(ast, scope):
        return FlushStatement()

    def run(self, *, context, frame):
        yield


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

    def preflight(self, *, context, frame):
        request = context.peek_request()
        assert request.message_type == "function_call"
        for value_expr, (parameter, value) in zip(self.parameters, request.parameters):
            value_expr.evaluate(frame=frame).resolve(value)
        if request.accept_callbacks or request.function_signature.return_type:
            context.advance()
        context.complete_request()
        if context.interface.signature.callbacks:
            while True:
                callback = context.pop_callback()
                if callback is None:
                    break
                logger.debug(f"preflight callback {callback}")
                callback.preflight(context=context)

        if self.function.signature.return_type:
            return_value = self.return_value.evaluate(frame=frame).get()
        else:
            return_value = None
        context.send_response(FunctionReturn(
            return_value=return_value
        ))

    def run(self, *, context, frame):
        if context.interface.signature.callbacks:
            while True:
                logger.debug("accepting callbacks...")
                callback_name = context.process_connection.upward_pipe.readline().strip()
                logger.debug(f"received line {callback_name}")
                if callback_name == "return":
                    context.push_callback(None)
                    break
                else:
                    callback = context.interface.body.scope.callbacks[callback_name]
                    context.push_callback(callback)
                    yield from callback.run(context=context)
        yield from []


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

    def run(self, *, context, frame):
        size = self.index.range.evaluate(frame=frame).get()
        for i in range(size):
            with context.new_frame(scope=self.scope, parent=frame) as for_frame:
                for_frame[self.index.variable] = i
                yield from run_body(self.body, context=context, frame=for_frame)


def preflight_body(body, *, context, frame):
    with context.new_frame(parent=frame, scope=body.scope) as inner_frame:
        for statement in body.statements:
            if isinstance(statement, ImperativeStatement):
                logger.debug(f"preflight {statement}")
                statement.preflight(context=context, frame=inner_frame)


def run_body(body, *, context, frame):
    with context.new_frame(parent=frame, scope=body.scope) as inner_frame:
        for statement in body.statements:
            if isinstance(statement, ImperativeStatement):
                logger.debug(f"run {statement}")
                yield from statement.run(context=context, frame=inner_frame)
