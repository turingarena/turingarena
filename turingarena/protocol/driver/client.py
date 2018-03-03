import logging
from contextlib import contextmanager
from functools import partial

from turingarena.pipeboundary import PipeBoundary, PipeBoundarySide
from turingarena.protocol.driver.connection import DRIVER_QUEUE, DriverProcessConnection, DRIVER_PROCESS_CHANNEL
from turingarena.protocol.driver.serialize import MetaType, get_meta_type
from turingarena.protocol.exceptions import ProtocolExit
from turingarena.protocol.proxy import InterfaceProxy

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

    @contextmanager
    def connect(self):
        with self.boundary.open_channel(
                DRIVER_PROCESS_CHANNEL,
                PipeBoundarySide.CLIENT,
        ) as pipes:
            yield DriverProcessConnection(**pipes)


class DriverRunningProcess:
    def __init__(self, connection):
        self.connection = connection
        self.proxy = InterfaceProxy(self)

    def call(self, name, args, callbacks):
        logger.debug(f"call {name!r}, {args!r}, {callbacks.keys()!r}")
        callback_list = list(callbacks.items())

        with self.request() as p:
            p("function_call")

            p(name)

            p(len(args))
            for v in args:
                self.serialize(v, p)

            p(len(callback_list))
            for name, f in callback_list:
                p(name)
                p(f.__code__.co_argcount)

        logger.debug(f"call: request sent, waiting response")
        while self.read_response():  # has callback
            logger.debug(f"has callback, accepting")
            self.accept_callback(callback_list)

        if self.read_response():  # has return value
            return self.read_response()
        else:
            return None

    def accept_callback(self, callback_list):
        callback_index = self.read_response()
        name, f = callback_list[callback_index]
        logger.debug(f"received callback {name!r}, reading args...")
        args = [self.read_response() for _ in range(f.__code__.co_argcount)]
        logger.debug(f"received callback {name!r} with args {args!r}")
        try:
            return_value = f(*args)
        except ProtocolExit:
            with self.request() as p:
                p("exit")
            raise
        with self.request() as p:
            p("callback_return")
            p(name)
            has_return_value = (return_value is not None)
            p(int(has_return_value))
            if has_return_value:
                p(int(return_value))

    def read_response(self):
        line = self.connection.response.readline()
        assert line
        return int(line.strip())

    def serialize(self, value, p):
        meta_type = get_meta_type(value)
        logger.debug(f"meta_type: {meta_type!r}")
        p(meta_type.value)
        if meta_type is MetaType.ARRAY:
            items = list(value)
            p(len(items))
            for item in items:
                self.serialize(item, p)
        elif meta_type == MetaType.SCALAR:
            p(int(value))

    @contextmanager
    def request(self):
        yield partial(print, file=self.connection.request)
        self.connection.request.flush()

    def begin_main(self, global_variables):
        with self.request() as p:
            p("main_begin")
            p(len(global_variables))
            for name, value in global_variables.items():
                p(name)
                self.serialize(value, p)

    def end_main(self):
        with self.request() as p:
            p("main_end")
