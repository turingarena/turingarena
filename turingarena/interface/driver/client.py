import logging
from contextlib import contextmanager

from turingarena.interface.driver.commands import MetaType, get_meta_type
from turingarena.interface.driver.connection import DRIVER_QUEUE, DRIVER_PROCESS_QUEUE
from turingarena.interface.proxy import InterfaceProxy
from turingarena.pipeboundary import PipeBoundary

logger = logging.getLogger(__name__)


class DriverClient:
    def __init__(self, driver_dir):
        self.boundary = PipeBoundary(driver_dir)

    @contextmanager
    def run(self, *, interface_text, sandbox_process_dir):
        response = self.boundary.send_request(
            DRIVER_QUEUE,
            interface_text=interface_text,
            sandbox_process_dir=sandbox_process_dir,
        )
        yield response["driver_process_dir"]


class DriverProcessClient:
    def __init__(self, driver_process_dir):
        self.boundary = PipeBoundary(driver_process_dir)
        self.proxy = InterfaceProxy(self)

    def call(self, name, args, callbacks):
        callback_list = list(callbacks.items())
        response = self.send_call(args, name, callback_list)
        while True:
            response_it = self.response_iterator(response)
            if next(response_it):  # has callback
                index = next(response_it)
                args = list(response_it)
                name, f = callback_list[index]
                logger.debug(f"got callback {name!r:.20} with args {args!r:.20}")
                return_value = f(*args)
                response = self.send_callback_return(name, return_value)
            else:  # no callbacks
                break

        if next(response_it):  # has return value
            logger.debug(f"has return value, receiving...")
            return next(response_it)
        else:
            logger.debug(f"no return value, done")
            return None

    def send_call(self, args, name, callback_list):
        logger.debug(f"call {name!r}, {args!r}, {callback_list!r}")
        logger.debug(f"sending function call request")
        request_lines = call_request_lines(name, args, callback_list)
        return self.send_request(request_lines)

    def send_callback_return(self, name, return_value):
        logger.debug(f"sending callback return request")
        logger.debug(f"(callback {name!r:.20} returned {return_value!r:.10})")
        return self.send_request(callback_return_request_lines(name, return_value))

    def send_begin_main(self, global_variables):
        return self.send_request(begin_main_request_lines(global_variables))

    def send_end_main(self):
        return self.send_request(["main_end"])

    def send_exit(self):
        return self.send_request(["exit"])

    def send_request(self, request_lines):
        request = "\n".join(str(l) for l in request_lines)
        logger.debug(f"sending request:\n{request!s:.50}")
        response = self.boundary.send_request(
            DRIVER_PROCESS_QUEUE,
            request=request,
        )["response"]
        logger.debug(f"request:\n{request!s:.50}\ngot response:\n{response!s:.50}")
        return response

    def response_iterator(self, response):
        items = [int(line.strip()) for line in response.splitlines()]
        return iter(items)


def begin_main_request_lines(global_variables):
    yield "main_begin"
    yield len(global_variables)

    for name, value in global_variables.items():
        yield name
        yield from serialize(value)


def call_request_lines(name, args, callback_list):
    yield "function_call"
    yield name
    yield len(args)
    for value in args:
        yield from serialize(value)
    yield len(callback_list)
    for name, f in callback_list:
        yield name
        yield f.__code__.co_argcount


def callback_return_request_lines(callback_name, return_value):
    yield "callback_return"
    yield callback_name
    has_return_value = (return_value is not None)
    yield int(has_return_value)
    if has_return_value:
        yield int(return_value)


def serialize(value):
    meta_type = get_meta_type(value)
    logger.debug(f"meta_type: {meta_type!r}")
    yield meta_type.value
    if meta_type is MetaType.ARRAY:
        items = list(value)
        yield len(items)
        for item in items:
            yield from serialize(item)
    elif meta_type == MetaType.SCALAR:
        yield int(value)
