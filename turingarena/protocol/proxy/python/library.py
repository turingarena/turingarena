import logging

from turingarena.protocol.eval.commands import MainBegin, FunctionCall, ProxyResponse, CallbackReturn, MainEnd

logger = logging.getLogger(__name__)


class ProxyException(Exception):
    pass


class ProxyEngine:
    def __init__(self, *, interface, instance, connection):
        self.interface = interface
        self.instance = instance
        self.connection = connection
        self.main_begun = False

    def call(self, name, args, callbacks_impl):
        if not self.main_begun:
            self.begin_main()

        fun = self.interface.body.scope.functions[name]

        request = FunctionCall(
            function_signature=fun,
            parameters=args,
            accept_callbacks=bool(callbacks_impl),
        )
        self.send(request)

        while True:
            response = ProxyResponse.receive(self.connection.response_pipe)
            if response.response_type == "callback_call":
                return_value = callbacks_impl[response.callback_name](response.parameters)
                request = CallbackReturn(
                    return_value=return_value,
                )
                self.send(request)
                continue
            if response.response_type == "function_return":
                return response.return_value

    def send(self, request):
        request.send(self.connection.request_pipe)

    def begin_main(self):
        request = MainBegin(global_variables=[
            getattr(self.instance, variable_name)
            for variable_name in self.interface.body.scope.variables
        ])
        self.send(request)
        self.main_begun = True

    def end_main(self):
        assert self.main_begun
        request = MainEnd()
        self.send(request)
