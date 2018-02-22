import logging
import os
import subprocess
from contextlib import contextmanager, ExitStack

from turingarena.protocol.connection import DriverConnection
from turingarena.protocol.driver.commands import FunctionCall, CallbackReturn, ProxyResponse, MainBegin, MainEnd, Exit
from turingarena.protocol.exceptions import ProtocolError, ProtocolExit, CommunicationBroken
from turingarena.sandbox.exceptions import AlgorithmRuntimeError

logger = logging.getLogger(__name__)


class DriverClient:
    def __init__(self, *, interface, process):
        self.interface = interface
        self.process = process

    @contextmanager
    def connect(self):
        cli = [
            "turingarena-driver",
            self.interface,
            self.process.sandbox_dir,
        ]
        with ExitStack() as stack:
            logger.debug(f"running {cli}...")
            driver_process = subprocess.Popen(
                cli,
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )
            stack.enter_context(driver_process)
            driver_dir = driver_process.stdout.readline().strip()
            logger.debug(f"driver dir: {driver_dir}...")

            assert os.path.isdir(driver_dir)

            logger.debug("opening request pipe...")
            request_pipe = stack.enter_context(open(os.path.join(driver_dir, "driver_request.pipe"), "w"))
            logger.debug("opening response pipe...")
            response_pipe = stack.enter_context(open(os.path.join(driver_dir, "driver_response.pipe")))
            logger.debug("opening error pipe...")
            error_pipe = stack.enter_context(open(os.path.join(driver_dir, "error.pipe")))
            logger.debug("driver connected")

            try:
                yield DriverConnection(
                    request_pipe=request_pipe,
                    response_pipe=response_pipe,
                    error_pipe=error_pipe,
                )
            except Exception as e:
                logger.exception(e)
                raise

            logger.debug("waiting for driver server process")


class DriverClientEngine:
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
        try:
            return ProxyResponse.accept(
                map(str.strip, self.connection.response_pipe),
                interface_signature=self.interface_signature,
            )
        except CommunicationBroken:
            self.handle_exceptions()
            raise

    def send(self, request):
        try:
            file = self.connection.request_pipe
            for line in request.serialize():
                print(line, file=file)
            file.flush()
        except BrokenPipeError:
            raise CommunicationBroken

    def handle_exceptions(self):
        error = self.connection.error_pipe.read()
        if error:
            raise AlgorithmRuntimeError(error)

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


