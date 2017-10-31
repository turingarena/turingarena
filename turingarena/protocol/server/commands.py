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
                (variable, variable.type.deserialize(file=file))
                for variable in interface_signature.variables
            ]
        )

    def send_arguments(self, *, file):
        for variable, value in self.global_variables:
            variable.type.serialize(value, file=file)


@request_type("function_call")
class FunctionCall(ProxyRequest):
    __slots__ = ["function_name", "parameters", "accept_callbacks"]

    def send_arguments(self, *, file):
        print(self.function_name, file=file)
        for parameter, value in self.parameters:
            parameter.type.serialize(value, file=file)
        print(int(self.accept_callbacks), file=file)

    @staticmethod
    def receive_arguments(*, interface_signature, file):
        function_name = file.readline().strip()
        function_signature = interface_signature.functions[function_name]
        return FunctionCall(
            function_name=function_name,
            parameters=[
                (p, p.type.deserialize(file=file))
                for p in function_signature.parameters
            ],
            accept_callbacks=bool(int(file.readline().strip())),
        )


@request_type("callback_return")
class CallbackReturn(ProxyRequest):
    __slots__ = ["return_value"]


@request_type("main_end")
class MainEnd(ProxyRequest):
    __slots__ = []


class ProxyResponse(ProxyMessage):
    __slots__ = []
    message_types = response_types


@request_type("function_return")
class FunctionReturn(ProxyResponse):
    __slots__ = ["return_value"]


@request_type("callback_call")
class CallbackCall(ProxyResponse):
    __slots__ = ["callback", "parameters"]
