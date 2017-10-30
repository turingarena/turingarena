from bidict import bidict

from turingarena.protocol.model.node import ImmutableObject

request_types = bidict()


def request_type(statement_type):
    def decorator(cls):
        request_types[statement_type] = cls
        return cls

    return decorator


class ProxyRequest(ImmutableObject):
    __slots__ = []

    @staticmethod
    def accept_any(*, interface, pipe):
        line = pipe.readline()
        assert line
        request_type = line.strip()
        return request_types[request_type].parse(
            interface=interface,
            pipe=pipe,
        )

    @classmethod
    def accept(cls, **kwargs):
        request = ProxyRequest.accept_any(**kwargs)
        assert isinstance(request, cls)
        return request


@request_type("global_data_init")
class GlobalDataInit(ProxyRequest):
    __slots__ = ["values"]


@request_type("function_call")
class FunctionCall(ProxyRequest):
    __slots__ = ["function", "parameters", "has_callbacks"]


@request_type("callback_end")
class CallbackEnd(ProxyRequest):
    __slots__ = []


@request_type("callback_return")
class CallbackReturn(ProxyRequest):
    __slots__ = ["value"]


@request_type("main_end")
class MainEnd(ProxyRequest):
    __slots__ = []


class ProxyResponse(ImmutableObject):
    __slots__ = []


class FunctionEnd(ProxyResponse):
    __slots__ = []


class FunctionReturn(ProxyResponse):
    __slots__ = ["value"]


class CallbackCall(ProxyResponse):
    __slots__ = ["callback", "arguments"]
