import logging
from abc import abstractmethod

from bidict import bidict

from turingarena.common import ImmutableObject
from turingarena.protocol.exceptions import CommunicationBroken

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
    def accept(cls, lines, *, interface_signature):
        logger.debug("accepting message...")
        try:
            message_type = next(lines)
        except StopIteration:
            raise CommunicationBroken
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
        logger.debug(f"received message {message}")
        return message

    @abstractmethod
    def serialize_arguments(self):
        pass

    def serialize(self):
        logger.debug(f"serializing message {self}")
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
        return dict(
            global_variables=[
                variable.value_type.deserialize(lines)
                for variable in interface_signature.variables.values()
            ]
        )

    def serialize_arguments(self):
        for variable, value in zip(self.interface_signature.variables.values(), self.global_variables):
            yield from variable.value_type.serialize(value)


@request_type("function_call")
class FunctionCall(ProxyRequest):
    __slots__ = ["function_name", "parameters", "accept_callbacks"]

    @property
    def function_signature(self):
        return self.interface_signature.functions[self.function_name]

    def serialize_arguments(self):
        yield self.function_name
        for parameter, value in zip(self.function_signature.parameters, self.parameters):
            yield from parameter.value_type.serialize(value)
        yield str(int(self.accept_callbacks))

    @staticmethod
    def deserialize_arguments(lines, *, interface_signature):
        function_name = next(lines)
        function_signature = interface_signature.functions[function_name]
        parameters = [
            p.value_type.deserialize(lines)
            for p in function_signature.parameters
        ]
        accept_callbacks = bool(int(next(lines)))
        return dict(
            function_name=function_name,
            parameters=parameters,
            accept_callbacks=accept_callbacks,
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
        if callback_signature.return_type:
            return_value = callback_signature.return_type.deserialize(lines)
        else:
            return_value = None
        return dict(
            callback_name=callback_name,
            return_value=return_value,
        )

    def serialize_arguments(self):
        yield self.callback_name
        if self.return_type is not None:
            yield from self.return_type.serialize(self.return_value)


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
