import logging
from abc import abstractmethod

from bidict import bidict

from turingarena.common import ImmutableObject
from turingarena.protocol.driver.commands import FunctionReturn
from turingarena.protocol.driver.frames import Phase, RootBlockContext
from turingarena.protocol.exceptions import ProtocolExit, ProtocolError, CommunicationBroken
from turingarena.protocol.model.expressions import Expression
from turingarena.protocol.model.model import Main, Variable, Interface, Function, Callback
from turingarena.protocol.model.node import AbstractSyntaxNode
from turingarena.protocol.model.scope import Scope
from turingarena.protocol.model.type_expressions import ValueType, ScalarType, ArrayType

logger = logging.getLogger(__name__)

statement_classes = bidict()

ExitCall = object()


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
    __slots__ = []

    def run(self, context):
        yield from []

    def first_calls(self):
        return {None}


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

    def run(self, context):
        if context.phase is Phase.RUN:
            size = context.evaluate(self.size).get()
            for a in self.arguments:
                context.evaluate(a).alloc(size=size)
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

    def run(self, context):
        if context.phase is Phase.RUN:
            self.on_run(context)
        yield from []

    @abstractmethod
    def on_run(self, context):
        pass


@statement_class("input")
class InputStatement(InputOutputStatement):
    __slots__ = []

    def on_run(self, context):
        raw_values = [
            a.value_type.format(a.evaluate(frame=context.frame).get())
            for a in self.arguments
        ]
        logger.debug(f"printing {raw_values} to downward_pipe")
        # FIXME: should flush only once per communication block
        print(*raw_values, file=context.engine.process_connection.downward_pipe, flush=True)


@statement_class("output")
class OutputStatement(InputOutputStatement):
    __slots__ = []

    def on_run(self, context):
        logger.debug(f"reading from upward_pipe...")
        line = context.engine.process_connection.upward_pipe.readline()
        if not line:
            raise CommunicationBroken
        logger.debug(f"read line {line.strip()} from upward_pipe")
        raw_values = line.strip().split()
        logger.debug(f"read values {raw_values} from upward_pipe")
        for a, v in zip(self.arguments, raw_values):
            value = a.value_type.parse(v)
            context.evaluate(a).resolve(value)


@statement_class("flush")
class FlushStatement(ImperativeStatement):
    __slots__ = []

    @staticmethod
    def compile(ast, scope):
        return FlushStatement()

    def run(self, context):
        if context.phase is Phase.RUN:
            yield
        else:
            context.engine.flush()


@statement_class("call")
class CallStatement(ImperativeStatement):
    __slots__ = ["function", "parameters", "return_value"]

    @staticmethod
    def compile(ast, scope):
        fun = scope.functions[ast.function_name]
        assert len(ast.parameters) == len(fun.signature.parameters)
        if ast.return_value is None:
            return_value = None
        else:
            return_value = Expression.compile(
                ast.return_value,
                scope=scope,
                expected_type=fun.signature.return_type,
            )
        return CallStatement(
            function=fun,
            parameters=[
                Expression.compile(arg, scope=scope, expected_type=decl_arg.value_type)
                for decl_arg, arg in zip(fun.signature.parameters, ast.parameters)
            ],
            return_value=return_value,
        )

    def preflight(self, context):
        request = context.engine.process_request(expected_type="function_call")

        if request.function_name != self.function.name:
            raise ProtocolError(f"expected call to '{self.function.name}', got '{request.function_name}'")

        for value_expr, value in zip(self.parameters, request.parameters):
            context.evaluate(value_expr).resolve(value)

        return_type = self.function.signature.return_type
        if return_type or request.accept_callbacks:
            context.engine.ensure_output()

        yield from self.invoke_callbacks(context)

        if return_type:
            return_value = context.evaluate(self.return_value).get()
        else:
            return_value = None
        context.engine.send_response(FunctionReturn(
            interface_signature=context.engine.interface.signature,
            function_name=self.function.name,
            return_value=return_value,
        ))

    def accept_callbacks(self, context):
        if not context.engine.interface.signature.callbacks:
            return
        while True:
            logger.debug("accepting callbacks...")
            callback_name = context.engine.process_connection.upward_pipe.readline().strip()
            logger.debug(f"received line {callback_name}")
            if callback_name == "return":
                logger.debug(f"no more callbacks, push None to callback queue")
                context.engine.push_callback(None)
                break
            else:
                callback = context.engine.interface.body.scope.callbacks[callback_name]
                callback_context = RootBlockContext(callback)
                context.engine.push_callback(callback_context)
                logger.debug(f"got callback '{callback_name}', pushing to queue")
                yield from callback.run(context=context.engine.new_context(
                    root_block_context=callback_context,
                    phase=context.phase,
                ))

    def invoke_callbacks(self, context):
        if not context.engine.interface.signature.callbacks:
            logger.debug(f"no callback defined, nothing to do")
            return
        while True:
            logger.debug(f"popping callbacks")
            callback_context = context.engine.pop_callback()
            logger.debug(f"popped {callback_context}")
            if callback_context is None:
                break
            yield from callback_context.callback.run(context.engine.new_context(
                root_block_context=callback_context,
                phase=context.phase,
            ))
            context.engine.ensure_output()

    def run(self, context):
        if context.phase is Phase.RUN:
            yield from self.accept_callbacks(context)
        if context.phase is Phase.PREFLIGHT:
            yield from self.preflight(context)

    def first_calls(self):
        return {self.function.name}


@statement_class("return")
class ReturnStatement(ImperativeStatement):
    __slots__ = ["value"]

    @staticmethod
    def compile(ast, scope):
        return ReturnStatement(
            value=Expression.compile(ast.value, scope=scope),
        )

    def run(self, context):
        if context.phase is Phase.PREFLIGHT:
            request = context.engine.peek_request(expected_type="callback_return")
            context.evaluate(self.value).resolve(request.return_value)
        yield from []


@statement_class("exit")
class ExitStatement(ImperativeStatement):
    __slots__ = []

    @staticmethod
    def compile(ast, scope):
        return ExitStatement()

    def run(self, context):
        yield from []
        if context.phase == Phase.PREFLIGHT:
            context.engine.ensure_output()
        raise ProtocolExit

    def first_calls(self):
        return {ExitCall}


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

    def run(self, context):
        if context.phase is Phase.RUN or self.may_call():
            size = context.evaluate(self.index.range).get()
            for i in range(size):
                with context.enter(self.scope) as inner_context:
                    inner_context.frame[self.index.variable] = i
                    yield from self.body.run(inner_context)

    def may_call(self):
        return any(f is not None for f in self.body.first_calls())

    def first_calls(self):
        return self.body.first_calls() | {None}


@statement_class("if")
class IfStatement(ImperativeStatement):
    __slots__ = ["condition", "then_body", "else_body"]

    @staticmethod
    def compile(ast, scope):
        return IfStatement(
            condition=Expression.compile(ast.condition, scope=scope),
            then_body=Body.compile(ast.then_body, scope=scope),
            else_body=(
                None if ast.else_body is None else
                Body.compile(ast.then_body, scope=scope)
            ),
        )

    def run(self, context):
        condition = context.evaluate(self.condition)
        if context.phase == Phase.PREFLIGHT and not condition.is_resolved():
            # FIXME: use a stricter logic here
            if self.then_body.is_possible_branch(context=context):
                condition.resolve(1)
            else:
                condition.resolve(0)

        if condition.get():
            yield from self.then_body.run(context)
        elif self.else_body is not None:
            yield from self.else_body.run(context)

    def first_calls(self):
        return self.then_body.first_calls() | (
            {None} if self.else_body is not None else
            self.else_body.first_calls()
        )


@statement_class("loop")
class LoopStatement(ImperativeStatement):
    __slots__ = ["body"]

    @staticmethod
    def compile(ast, scope):
        return LoopStatement(
            body=Body.compile(ast.body, scope=scope),
        )

    def run(self, context):
        if context.phase is Phase.RUN or self.may_call():
            size = context.evaluate(self.index.range).get()
            for i in range(size):
                with context.enter(self.scope) as inner_context:
                    inner_context.frame[self.index.variable] = i
                    yield from self.body.run(inner_context)

    def first_calls(self):
        return self.body.first_calls() | {None}


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

    def run(self, context):
        logger.debug(f"running body")
        with context.enter(self.scope) as inner_context:
            for statement in self.statements:
                if isinstance(statement, ImperativeStatement):
                    yield from statement.run(inner_context)

    def is_possible_branch(self, *, context):
        request = context.engine.peek_request()
        if request.message_type == "function_call":
            call = request.function_name
        elif request.message_type == "exit":
            call = ExitCall
        else:
            call = None
        return call is not None and call in self.first_calls()

    def first_calls(self):
        ans = {None}
        for s in self.statements:
            if None not in ans:
                break
            ans.remove(None)
            ans.update(s.first_calls())
        return ans
