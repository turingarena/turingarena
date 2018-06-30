import logging
from collections import namedtuple

from turingarena import AlgorithmRuntimeError
from turingarena.driver.commands import serialize_data
from turingarena.processinfo import SandboxProcessInfo

CallRequest = namedtuple("CallRequest", ["method_name", "arguments", "has_return_value", "callbacks"])


class DriverClientEngine:
    __slots__ = ["process", "connection", "phase"]

    def __init__(self, process, connection):
        self.process = process
        self.connection = connection

    def get_info(self, kill=False):
        self.get_response_ok()
        self.send_request("wait")
        self.send_request(int(kill))

        return self.do_get_info()

    def do_get_info(self):
        time_usage = float(self.get_response_line())
        memory_usage = int(self.get_response_line())
        return SandboxProcessInfo(
            time_usage=time_usage,
            memory_usage=memory_usage,
            error=None,
        )

    def call(self, request):
        self._send_next_request()
        for line in self.call_lines(request):
            self.send_request(line)

        self.accept_callbacks(request.callbacks)

        if request.has_return_value:
            logging.debug(f"Receiving return value...")
            return self.get_response_value()
        else:
            return None

    def get_response_line(self):
        self.connection.downward.flush()
        line = self.connection.upward.readline().strip()
        assert line
        logging.debug(f"Read response line: {line}")
        return line

    def get_response_value(self):
        return int(self.get_response_line())

    def get_response_ok(self):
        logging.debug(f"waiting for response ok")
        any_error = self.get_response_value()
        if any_error:
            info = self.do_get_info()
            message = self.get_response_line()
            raise AlgorithmRuntimeError(self.process, message, info)

    def accept_callbacks(self, callback_list):
        while True:
            if self.get_response_value():  # has callback
                logging.debug(f"has callback")
                index = self.get_response_value()
                callback = callback_list[index]
                args = [
                    int(self.get_response_value())
                    for _ in range(callback.__code__.co_argcount)
                ]
                return_value = callback(*args)
                logging.debug(f"callback {index} ({args}) -> {return_value}")
                self.send_callback_return(return_value)
            else:  # no callbacks
                break

    def call_lines(self, request):
        yield "call"
        yield request.method_name
        yield len(request.arguments)
        for a in request.arguments:
            yield from serialize_data(a)
        yield int(request.has_return_value)
        yield len(request.callbacks)
        for c in request.callbacks:
            yield c.__code__.co_argcount

    def send_callback_return(self, return_value):
        self._send_next_request()
        self.send_request("callback_return")
        if return_value is not None:
            self.send_request(1)
            self.send_request(int(return_value))
        else:
            self.send_request(0)

    def send_exit(self):
        self._send_next_request()
        self.send_request("exit")

    def send_checkpoint(self):
        self._send_next_request()
        self.send_request("checkpoint")

    def _send_next_request(self):
        self.get_response_ok()
        self.send_request("request")

    def send_request(self, line):
        logging.debug(f"sending request line: {line}")
        print(line, file=self.connection.downward)
