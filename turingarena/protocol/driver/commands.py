import logging
from abc import abstractmethod

from bidict import bidict

from turingarena.common import ImmutableObject
from turingarena.protocol.driver.serialize import deserialize

logger = logging.getLogger(__name__)

request_types = bidict()
response_types = bidict()


def request_type(name):
    def decorator(cls):
        request_types[name] = cls
        return cls

    return decorator


def response_type(name):
    def decorator(cls):
        response_types[name] = cls
        return cls

    return decorator


class ProxyMessage(ImmutableObject):
    __slots__ = ["interface_signature", "message_type"]

    message_types = None

    def __init__(self, **kwargs):
        kwargs.setdefault("message_type", self.message_types.inv[self.__class__])
        super().__init__(**kwargs)

    @staticmethod
    @abstractmethod
    def deserialize_arguments(lines, *, interface_signature):
        pass

    @classmethod
    def deserialize(cls, lines, *, interface_signature):
        logger.debug("accepting message...")
        message_type = next(lines)
        logger.debug(f"received message type {message_type}, parsing arguments...")
        cls2 = cls.message_types[message_type]
        arguments = cls2.deserialize_arguments(
            interface_signature=interface_signature,
            lines=lines,
        )
        message = cls2(
            interface_signature=interface_signature,
            **arguments,
        )
        return message

    def serialize_arguments(self):
        pass

    def serialize(self):
        yield self.message_type
        yield from self.serialize_arguments()


class ProxyRequest(ProxyMessage):
    __slots__ = []
    message_types = request_types


@request_type("main_begin")
class MainBegin(ProxyRequest):
    __slots__ = ["global_variables"]

    @staticmethod
    def deserialize_arguments(lines, *, interface_signature):
        size = int(next(lines))
        global_variables = dict([
            (next(lines), deserialize(lines))
            for _ in range(size)
        ])
        assert len(global_variables) == len(interface_signature.variables)
        return dict(
            global_variables=[
                variable.value_type.ensure(global_variables[name])
                for name, variable in interface_signature.variables.items()
            ]
        )


@request_type("function_call")
class FunctionCall(ProxyRequest):
    __slots__ = ["function_name", "parameters", "accepted_callbacks"]

    @property
    def function_signature(self):
        return self.interface_signature.functions[self.function_name]

    @staticmethod
    def deserialize_arguments(lines, *, interface_signature):
        function_name = next(lines)
        function_signature = interface_signature.functions[function_name]

        parameters_count = int(next(lines))
        assert parameters_count == len(function_signature.parameters)

        parameters = [
            p.value_type.ensure(deserialize(lines))
            for p in function_signature.parameters
        ]

        accepted_callbacks = list()
        callbacks_count = int(next(lines))
        for _ in range(callbacks_count):
            callback_name = next(lines)
            callback_parameters_count = int(next(lines))

            callback_signature = interface_signature.callbacks[callback_name]
            assert callback_parameters_count == len(callback_signature.parameters)

            accepted_callbacks.append(callback_name)

        return dict(
            function_name=function_name,
            parameters=parameters,
            accepted_callbacks=accepted_callbacks,
        )


@request_type("callback_return")
class CallbackReturn(ProxyRequest):
    __slots__ = ["callback_name", "return_value"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.return_type is not None:
            assert self.return_value is not None
        else:
            assert self.return_value is None

    @property
    def return_type(self):
        return self.callback_signature.return_type

    @property
    def callback_signature(self):
        return self.interface_signature.callbacks[self.callback_name]

    @staticmethod
    def deserialize_arguments(lines, *, interface_signature):
        callback_name = next(lines)
        callback_signature = interface_signature.callbacks[callback_name]
        has_return_value = int(next(lines))
        assert has_return_value == bool(callback_signature.return_type)
        if has_return_value:
            return_value = callback_signature.return_type.ensure(int(next(lines)))
        else:
            return_value = None
        return dict(
            callback_name=callback_name,
            return_value=return_value,
        )


@request_type("main_end")
class MainEnd(ProxyRequest):
    __slots__ = []

    @staticmethod
    def deserialize_arguments(lines, *, interface_signature):
        return dict()

    def serialize_arguments(self):
        yield from []


@request_type("exit")
class Exit(ProxyRequest):
    __slots__ = []

    @staticmethod
    def deserialize_arguments(lines, *, interface_signature):
        return dict()

    def serialize_arguments(self):
        yield from []


class ProxyResponse(ProxyMessage):
    __slots__ = []
    message_types = response_types


@response_type("function_return")
class FunctionReturn(ProxyResponse):
    __slots__ = ["function_name", "return_value"]

    @staticmethod
    def deserialize_arguments(lines, *, interface_signature):
        function_name = next(lines)
        signature = interface_signature.functions[function_name]
        if signature.return_type:
            return_value = signature.return_type.deserialize(lines)
        else:
            return_value = None
        return dict(
            function_name=function_name,
            return_value=return_value,
        )

    def serialize_arguments(self):
        yield self.function_name
        return_type = self.interface_signature.functions[self.function_name].return_type
        if self.return_value is not None:
            yield from return_type.serialize(self.return_value)


@response_type("callback_call")
class CallbackCall(ProxyResponse):
    __slots__ = ["callback_name", "parameters"]

    @staticmethod
    def deserialize_arguments(lines, *, interface_signature):
        callback_name = next(lines)
        callback_signature = interface_signature.callbacks[callback_name]
        return dict(
            callback_name=callback_name,
            parameters=[
                p.value_type.deserialize(lines)
                for p in callback_signature.parameters
            ],
        )

    def serialize_arguments(self):
        yield self.callback_name
        callback_signature = self.interface_signature.callbacks[self.callback_name]
        for p, v in zip(callback_signature.parameters, self.parameters):
            yield from p.value_type.serialize(v)
