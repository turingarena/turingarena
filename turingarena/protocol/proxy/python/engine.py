import logging
from contextlib import contextmanager
from functools import partial

from turingarena.protocol.server.commands import MainBegin, FunctionCall, ProxyResponse, CallbackReturn, MainEnd

logger = logging.getLogger(__name__)


class ProxyException(Exception):
    pass


class ProxyEngine:
    def __init__(self, *, interface_signature, connection):
        self.interface_signature = interface_signature
        self.connection = connection

    def call(self, name, args, callbacks_impl):
        function_signature = self.interface_signature.functions[name]

        request = FunctionCall(
            interface_signature=self.interface_signature,
            function_name=name,
            parameters=[
                p.value_type.ensure(a)
                for p, a in zip(function_signature.parameters, args)
            ],
            accept_callbacks=bool(callbacks_impl),
        )
        self.send(request)

        while True:
            logger.debug("waiting for response...")
            response = self.accept_response()
            if response.message_type == "callback_call":
                callback_name = response.callback_name
                callback_signature = self.interface_signature.callbacks[callback_name]
                raw_return_value = callbacks_impl[callback_name](*response.parameters)
                return_type = callback_signature.return_type
                if return_type:
                    return_value = return_type.ensure(raw_return_value)
                else:
                    assert raw_return_value is None
                    return_value = None
                request = CallbackReturn(
                    interface_signature=self.interface_signature,
                    callback_name=callback_name,
                    return_value=return_value,
                )
                self.send(request)
                continue
            if response.message_type == "function_return":
                return response.return_value

    def accept_response(self):
        return ProxyResponse.accept(
            map(str.strip, self.connection.response_pipe),
            interface_signature=self.interface_signature,
        )

    def send(self, request):
        file = self.connection.request_pipe
        for line in request.serialize():
            print(line, file=file)
        file.flush()

    def begin_main(self, **global_variables):
        request = MainBegin(
            interface_signature=self.interface_signature,
            global_variables=[
                global_variables[variable.name]
                for variable in self.interface_signature.variables.values()
            ]
        )
        self.send(request)

    def end_main(self):
        request = MainEnd(
            interface_signature=self.interface_signature,
        )
        self.send(request)


class Proxy:
    def __init__(self, engine, interface_signature):
        self._engine = engine
        self._interface_signature = interface_signature

    def __getattr__(self, item):
        try:
            fun = self._interface_signature.functions[item]
        except KeyError:
            raise AttributeError

        def method(*args, **kwargs):
            return self._engine.call(item, args=args, callbacks_impl=kwargs)

        return method
