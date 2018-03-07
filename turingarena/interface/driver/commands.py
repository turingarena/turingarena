import collections
import logging
import numbers
from abc import abstractmethod
from enum import IntEnum

from bidict import bidict

from turingarena.common import ImmutableObject

logger = logging.getLogger(__name__)


class ProxyRequest(ImmutableObject):
    __slots__ = ["interface_signature", "request_type"]

    def __init__(self, **kwargs):
        kwargs.setdefault("request_type", request_types.inv[self.__class__])
        super().__init__(**kwargs)

    @staticmethod
    @abstractmethod
    def deserialize_arguments(lines, *, interface_signature):
        pass

    @classmethod
    def deserialize(cls, lines, *, interface_signature):
        logger.debug("accepting request...")
        request_type = next(lines)
        logger.debug(f"received request type {request_type}, parsing arguments...")
        cls2 = request_types[request_type]
        arguments = cls2.deserialize_arguments(
            interface_signature=interface_signature,
            lines=lines,
        )
        message = cls2(
            interface_signature=interface_signature,
            **arguments,
        )
        return message


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


class FunctionCall(ProxyRequest):
    __slots__ = ["function_name", "parameters", "accepted_callbacks"]

    @property
    def function_signature(self):
        return self.interface_signature.functions[self.function_name]

    @staticmethod
    def deserialize_arguments(lines, *, interface_signature):
        logger.debug(f"deserializing FunctionCall...")
        function_name = next(lines)
        function_signature = interface_signature.functions[function_name]

        logger.debug(f"read name {function_name!r}")
        parameters_count = int(next(lines))
        assert parameters_count == len(function_signature.parameters)

        parameters = [
            p.value_type.ensure(deserialize(lines))
            for p in function_signature.parameters
        ]
        logger.debug(f"read parameters: {parameters!r:.50s}")

        accepted_callbacks = list()
        callbacks_count = int(next(lines))
        for _ in range(callbacks_count):
            callback_name = next(lines)
            callback_parameters_count = int(next(lines))

            callback_signature = interface_signature.callbacks[callback_name]
            assert callback_parameters_count == len(callback_signature.parameters)

            accepted_callbacks.append(callback_name)

        logger.debug(f"read accepted_callbacks: {accepted_callbacks!r:.50s}")
        return dict(
            function_name=function_name,
            parameters=parameters,
            accepted_callbacks=accepted_callbacks,
        )


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
        has_return_value = bool(int(next(lines)))
        assert has_return_value == bool(callback_signature.return_type)
        if has_return_value:
            return_value = callback_signature.return_type.ensure(int(next(lines)))
        else:
            return_value = None
        logger.debug(f"callback return: {callback_name!r:.10} -> {return_value!r:.10}")
        return dict(
            callback_name=callback_name,
            return_value=return_value,
        )


class MainEnd(ProxyRequest):
    __slots__ = []

    @staticmethod
    def deserialize_arguments(lines, *, interface_signature):
        return dict()


class Exit(ProxyRequest):
    __slots__ = []

    @staticmethod
    def deserialize_arguments(lines, *, interface_signature):
        return dict()


request_types = bidict({
    "main_begin": MainBegin,
    "main_end": MainEnd,
    "function_call": FunctionCall,
    "callback_return": CallbackReturn,
    "exit": Exit,
})


class MetaType(IntEnum):
    SCALAR = 0
    ARRAY = 1


def get_meta_type(value):
    if isinstance(value, collections.Iterable):
        return MetaType.ARRAY
    if isinstance(value, numbers.Integral):
        return MetaType.SCALAR
    raise AssertionError(f"unsupported type for value: {value}")


def deserialize(lines):
    meta_type = MetaType(int(next(lines)))
    if meta_type is MetaType.ARRAY:
        size = int(next(lines))
        return [deserialize(lines) for _ in range(size)]
    elif meta_type == MetaType.SCALAR:
        return int(next(lines))
