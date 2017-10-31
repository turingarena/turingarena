import logging

from turingarena.protocol.server.commands import MainBegin, FunctionCall, ProxyResponse, CallbackReturn, MainEnd

logger = logging.getLogger(__name__)


class ProxyException(Exception):
    pass


class ProxyEngine:
    def __init__(self, *, interface_signature, instance, connection):
        self.interface_signature = interface_signature
        self.instance = instance
        self.connection = connection
        self.main_begun = False

    def call(self, name, args, callbacks_impl):
        if not self.main_begun:
            self.begin_main()

        function_signature = self.interface_signature.functions[name]

        request = FunctionCall(
            function_name=name,
            parameters=[
                (p, p.value_type.ensure(a))
                for p, a in zip(function_signature.parameters, args)
            ],
            accept_callbacks=bool(callbacks_impl),
        )
        self.send(request)

        while True:
            logger.debug("waiting for response...")
            response = ProxyResponse.accept(
                interface_signature=self.interface_signature,
                file=self.connection.response_pipe,
            )
            if response.message_type == "callback_call":
                callback_name = response.callback_name
                callback_signature = self.interface_signature.callbacks[callback_name]
                return_value = callbacks_impl[callback_name](*[
                    v for p, v in response.parameters
                ])
                if callback_signature.return_type:
                    return_type_value = callback_signature.return_type, return_value
                else:
                    return_type_value = None
                request = CallbackReturn(
                    callback_name=callback_name,
                    return_value=return_type_value,
                )
                self.send(request)
                continue
            if response.message_type == "function_return":
                return response.return_value

    def send(self, request):
        request.send(file=self.connection.request_pipe)

    def begin_main(self):
        request = MainBegin(global_variables=[
            (variable, getattr(self.instance, variable.name))
            for variable in self.interface_signature.variables
        ])
        self.send(request)
        self.main_begun = True

    def end_main(self):
        assert self.main_begun
        request = MainEnd()
        self.send(request)
