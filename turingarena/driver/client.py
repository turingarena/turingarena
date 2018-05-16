import logging
from contextlib import contextmanager

from turingarena import InterfaceError
from turingarena.driver.commands import serialize_request, Exit, FunctionCall, \
    CallbackReturn
from turingarena.driver.connection import DRIVER_QUEUE, DRIVER_PROCESS_QUEUE
from turingarena.driver.proxy import InterfaceProxy
from turingarena.pipeboundary import PipeBoundary

logger = logging.getLogger(__name__)


class SandboxError(Exception):
    pass


class DriverClient:
    def __init__(self, driver_dir):
        self.boundary = PipeBoundary(driver_dir)

    @contextmanager
    def run_driver(self, *, interface_name, sandbox_process_dir):
        response = self.boundary.send_request(
            DRIVER_QUEUE,
            interface_name=interface_name,
            sandbox_process_dir=sandbox_process_dir,
        )
        yield response["driver_process_dir"]


class DriverProcessClient:
    def __init__(self, driver_process_dir):
        self.boundary = PipeBoundary(driver_process_dir)
        self.proxy = InterfaceProxy(self)

    def call(self, name, args):
        response = self.send_call(args, name)
        while True:
            response_it = self.response_iterator(response)
            if next(response_it):  # has callback
                index = next(response_it)
                args = list(response_it)
                name, f = callback_list[index]
                return_value = f(*args)
                response = self.send_callback_return(return_value)
            else:  # no callbacks
                break

        if next(response_it):  # has return value
            return next(response_it)
        else:
            return None

    def send_call(self, args, name):
        return self.send_request(FunctionCall(
            function_name=name,
            parameters=args,
        ))

    def send_callback_return(self, return_value):
        return self.send_request(CallbackReturn(return_value=return_value))

    def send_exit(self):
        return self.send_request(Exit())

    def send_request(self, request):
        request_payload = "\n".join(str(l) for l in serialize_request(request))
        payloads = self.boundary.send_request(DRIVER_PROCESS_QUEUE, request=request_payload)

        driver_error = payloads["driver_error"]
        if driver_error:
            raise InterfaceError(driver_error)
        sandbox_error = payloads["sandbox_error"]
        if sandbox_error:
            raise SandboxError(sandbox_error)

        return payloads["response"]

    def response_iterator(self, response):
        items = [int(line.strip()) for line in response.splitlines()]
        return iter(items)
