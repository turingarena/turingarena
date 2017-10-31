import logging
from abc import abstractmethod

from bidict import bidict

from turingarena.protocol.model.node import ImmutableObject

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
    __slots__ = ["message_type"]
    message_types = None

    def __init__(self, **kwargs):
        super().__init__(message_type=self.message_types.inv[self.__class__], **kwargs)

    @staticmethod
    @abstractmethod
    def receive_arguments(*, interface_signature, file):
        pass

    @classmethod
    def accept(cls, *, interface_signature, file):
        logger.debug("accepting message...")
        line = file.readline()
        assert line
        message_type = line.strip()
        logger.debug(f"received message type {message_type}, parsing arguments...")
        message = cls.message_types[message_type].receive_arguments(
            interface_signature=interface_signature,
            file=file,
        )
        logger.debug(f"received message {message}")
        return message

    @abstractmethod
    def send_arguments(self, *, file):
        pass

    def send(self, *, file):
        logger.debug(f"sending message {self}")
        print(self.message_type, file=file)
        self.send_arguments(file=file)
        file.flush()


class ProxyRequest(ProxyMessage):
    __slots__ = []
    message_types = request_types


@request_type("main_begin")
class MainBegin(ProxyRequest):
    __slots__ = ["global_variables"]

    @staticmethod
    def receive_arguments(*, interface_signature, file):
        return MainBegin(
            global_variables=[
                (variable, variable.value_type.deserialize(file=file))
                for variable in interface_signature.variables
            ]
        )

    def send_arguments(self, *, file):
        for variable, value in self.global_variables:
            variable.value_type.serialize(value, file=file)


@request_type("function_call")
class FunctionCall(ProxyRequest):
    __slots__ = ["function_name", "parameters", "accept_callbacks"]

    def send_arguments(self, *, file):
        print(self.function_name, file=file)
        for parameter, value in self.parameters:
            parameter.value_type.serialize(value, file=file)
        print(int(self.accept_callbacks), file=file)

    @staticmethod
    def receive_arguments(*, interface_signature, file):
        function_name = file.readline().strip()
        function_signature = interface_signature.functions[function_name]
        parameters = [
            (p, p.value_type.deserialize(file=file))
            for p in function_signature.parameters
        ]
        accept_callbacks = bool(int(file.readline().strip()))
        return FunctionCall(
            function_name=function_name,
            parameters=parameters,
            accept_callbacks=accept_callbacks,
        )


@request_type("callback_return")
class CallbackReturn(ProxyRequest):
    __slots__ = ["callback_name", "return_value"]

    @staticmethod
    def receive_arguments(*, interface_signature, file):
        callback_name = file.readline().strip()
        callback_signature = interface_signature.callbacks[callback_name]
        if callback_signature.return_type:
            return_type_value = (
                callback_signature.return_type,
                callback_signature.return_type.deserialize(file=file),
            )
        else:
            return_type_value = None
        return CallbackReturn(
            callback_name=callback_name,
            return_value=return_type_value,
        )

    def send_arguments(self, *, file):
        print(self.callback_name, file=file)
        # FIXME: should type be deduced ?
        if self.return_value:
            return_type, return_value = self.return_value
            return_type.serialize(return_value, file=file)


@request_type("main_end")
class MainEnd(ProxyRequest):
    __slots__ = []


class ProxyResponse(ProxyMessage):
    __slots__ = []
    message_types = response_types


@response_type("function_return")
class FunctionReturn(ProxyResponse):
    __slots__ = ["return_value"]


@response_type("callback_call")
class CallbackCall(ProxyResponse):
    __slots__ = ["callback_name", "parameters"]

    @staticmethod
    def receive_arguments(*, interface_signature, file):
        name = file.readline().strip()
        signature = interface_signature.callbacks[name]
        return CallbackCall(
            callback_name=name,
            parameters=[
                (p, p.value_type.deserialize(file=file))
                for p in signature.parameters
            ],
        )

    def send_arguments(self, *, file):
        print(self.callback_name, file=file)
        for p, v in self.parameters:
            p.value_type.serialize(v, file=file)
