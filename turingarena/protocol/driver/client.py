import logging
from contextlib import contextmanager

from turingarena.pipeboundary import PipeBoundary, PipeBoundarySide
from turingarena.protocol.driver.commands import FunctionCall, CallbackReturn, ProxyResponse, MainBegin, MainEnd, Exit
from turingarena.protocol.driver.connection import DRIVER_QUEUE, DriverProcessConnection, DRIVER_PROCESS_CHANNEL
from turingarena.protocol.exceptions import ProtocolError, ProtocolExit
from turingarena.protocol.module import load_interface_signature

logger = logging.getLogger(__name__)


class DriverClient:
    def __init__(self, driver_dir):
        self.boundary = PipeBoundary(driver_dir)

    @contextmanager
    def run(self, *, interface, sandbox_process_dir):
        response = self.boundary.send_request(
            DRIVER_QUEUE,
            interface=interface,
            sandbox_process_dir=sandbox_process_dir,
        )

        driver_process_dir = response["driver_process_dir"]

        logger.info(f"connected to driver at {driver_process_dir}")

        try:
            yield driver_process_dir
        except Exception as e:
            logger.exception(e)
            raise


class DriverProcessClient:
    def __init__(self, *, interface, driver_process_dir):
        self.boundary = PipeBoundary(driver_process_dir)
        self.interface = interface

    @contextmanager
    def run(self):
        interface_signature = load_interface_signature(self.interface)
        with self.boundary.open_channel(
                DRIVER_PROCESS_CHANNEL,
                PipeBoundarySide.CLIENT,
        ) as pipes:
            connection = DriverProcessConnection(**pipes)
            yield DriverProcessEngine(
                interface_signature=interface_signature,
                connection=connection,
            )


class DriverProcessEngine:
    def __init__(self, *, interface_signature, connection):
        self.interface_signature = interface_signature
        self.connection = connection

    def call(self, name, args, callbacks_impl):
        try:
            function_signature = self.interface_signature.functions[name]
        except KeyError:
            raise ProtocolError(f"undefined function {name}")

        if len(args) != len(function_signature.parameters):
            raise ProtocolError(
                f"function '{name}'"
                f" expects {len(function_signature.parameters)} parameters,"
                f" got {len(args)}")

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
                self.accept_callback(callbacks_impl, response)
                continue
            if response.message_type == "function_return":
                return response.return_value

    def accept_callback(self, callbacks_impl, response):
        callback_name = response.callback_name
        callback_signature = self.interface_signature.callbacks[callback_name]
        try:
            raw_return_value = callbacks_impl[callback_name](*response.parameters)
        except ProtocolExit:
            request = Exit(interface_signature=self.interface_signature)
            self.send(request)
            raise
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

    def accept_response(self):
        return ProxyResponse.accept(
            map(str.strip, self.connection.response),
            interface_signature=self.interface_signature,
        )

    def send(self, request):
        file = self.connection.request
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
