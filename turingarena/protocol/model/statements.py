import logging

from bidict import bidict

from turingarena.protocol.model.expressions import Expression
from turingarena.protocol.model.model import Main, Variable, Interface, Function, Callback
from turingarena.protocol.model.node import AbstractSyntaxNode, ImmutableObject
from turingarena.protocol.model.scope import Scope
from turingarena.protocol.model.type_expressions import ValueType, ScalarType, ArrayType
from turingarena.protocol.server.commands import FunctionReturn
from turingarena.protocol.server.frames import Phase

logger = logging.getLogger(__name__)

statement_classes = bidict()


def statement_class(statement_type):
    def decorator(cls):
        statement_classes[statement_type] = cls
        return cls

    return decorator


class Statement(AbstractSyntaxNode):
    __slots__ = ["statement_type"]

    def __init__(self, **kwargs):
        super().__init__(statement_type=statement_classes.inv[self.__class__], **kwargs)

    @staticmethod
    def compile(ast, scope):
        logger.debug("compiling statement {}".format(ast))
        return statement_classes[ast.statement_type].compile(ast, scope)


@statement_class("var")
class VarStatement(Statement):
    __slots__ = ["value_type", "variables"]

    @staticmethod
    def compile(ast, scope):
        value_type = ValueType.compile(ast.type_expression, scope=scope)
        variables = [
            Variable(value_type=value_type, name=d.name)
            for d in ast.declarators
        ]
        for v in variables:
            scope.variables[v.name] = v
        return VarStatement(
            value_type=value_type,
            variables=variables
        )


@statement_class("interface")
class InterfaceStatement(Statement):
    __slots__ = ["interface"]

    @staticmethod
    def compile(ast, scope):
        interface = Interface.compile(ast, scope)
        scope.interfaces[interface.name] = interface
        return InterfaceStatement(interface=interface)


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


@statement_class("callback")
class CallbackStatement(Statement):
    __slots__ = ["callback"]

    @staticmethod
    def compile(ast, scope):
        callback = Callback.compile(ast, scope=scope)
        scope.callbacks[callback.name] = callback
        return CallbackStatement(callback=callback)


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

    def preflight(self, *, context, frame):
        context.flush()

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
                Expression.compile(arg, scope=scope, expected_type=decl_arg.value_type)
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
        assert request.function_name == self.function.name

        for value_expr, (parameter, value) in zip(self.parameters, request.parameters):
            value_expr.evaluate(frame=frame).resolve(value)

        return_type = self.function.signature.return_type
        if return_type or request.accept_callbacks:
            context.ensure_output()

        context.complete_request()

        if context.interface.signature.callbacks:
            while True:
                logger.debug(f"popping callbacks")
                callback = context.pop_callback()
                if callback is None:
                    break
                callback.preflight(context=context)
                context.ensure_output()

        if return_type:
            return_value = return_type, self.return_value.evaluate(frame=frame).get()
        else:
            return_value = None
        context.send_response(FunctionReturn(
            function_name=self.function.name,
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

    def preflight(self, *, context, frame):
        request = context.peek_request()
        return_type, return_value = request.return_value
        assert request.message_type == "callback_return"
        self.value.evaluate(frame=frame).resolve(return_value)


class ForIndex(ImmutableObject):
    __slots__ = ["variable", "range"]


@statement_class("for")
class ForStatement(ImperativeStatement):
    __slots__ = ["index", "body", "scope"]

    @staticmethod
    def compile(ast, scope):
        for_scope = Scope(scope)
        index_var = Variable(value_type=ScalarType(int), name=ast.index.declarator.name)
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
            with context.new_frame(scope=self.scope, parent=frame, phase=Phase.RUN) as for_frame:
                for_frame[self.index.variable] = i
                yield from run_body(self.body, context=context, frame=for_frame)


def preflight_body(body, *, context, frame):
    with context.new_frame(parent=frame, scope=body.scope, phase=Phase.PREFLIGHT) as inner_frame:
        for statement in body.statements:
            if isinstance(statement, ImperativeStatement):
                logger.debug(f"preflight {statement}")
                statement.preflight(context=context, frame=inner_frame)


def run_body(body, *, context, frame):
    with context.new_frame(parent=frame, scope=body.scope, phase=Phase.RUN) as inner_frame:
        for statement in body.statements:
            if isinstance(statement, ImperativeStatement):
                logger.debug(f"run {statement}")
                yield from statement.run(context=context, frame=inner_frame)


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
