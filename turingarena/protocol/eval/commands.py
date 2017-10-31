from bidict import bidict

from turingarena.protocol.model.node import ImmutableObject

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
    __slots__ = []


class ProxyRequest(ProxyMessage):
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


@request_type("main_begin")
class MainBegin(ProxyRequest):
    __slots__ = ["values"]


@request_type("function_call")
class FunctionCall(ProxyRequest):
    __slots__ = ["function_signature", "parameters", "accept_callbacks"]


@request_type("callback_return")
class CallbackReturn(ProxyRequest):
    __slots__ = ["return_value"]


@request_type("main_end")
class MainEnd(ProxyRequest):
    __slots__ = []


class ProxyResponse(ProxyMessage):
    __slots__ = []


@request_type("function_return")
class FunctionReturn(ProxyResponse):
    __slots__ = ["return_value"]


@request_type("callback_call")
class CallbackCall(ProxyResponse):
    __slots__ = ["callback", "parameters"]
