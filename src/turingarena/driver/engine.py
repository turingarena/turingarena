import logging
from collections import namedtuple

from turingarena.driver.commands import serialize_data
from turingarena.driver.exceptions import AlgorithmRuntimeError
from turingarena.driver.processinfo import SandboxProcessInfo

CallRequest = namedtuple("CallRequest", ["method_name", "arguments", "has_return_value", "callbacks"])


class DriverClientEngine:
    __slots__ = ["process", "connection"]

    def __init__(self, process, connection):
        self.process = process
        self.connection = connection

    def get_info(self, kill=False):
        self._wait_ready()
        self._send_request_line("wait")
        self._send_request_line(int(kill))

        return self._do_get_info()

    def call(self, request):
        self._send_next_request()
        for line in self._call_lines(request):
            self._send_request_line(line)

        self._accept_callbacks(request.callbacks)

        if request.has_return_value:
            logging.debug(f"Receiving return value...")
            return self._get_response_value()
        else:
            return None

    def callback_return(self, return_value):
        self._send_next_request()
        self._send_request_line("callback_return")
        if return_value is not None:
            self._send_request_line(1)
            self._send_request_line(int(return_value))
        else:
            self._send_request_line(0)

    def exit(self):
        self._send_next_request()
        self._send_request_line("exit")

    def stop(self):
        self._wait_ready()
        self._send_request_line("stop")
        self._wait_ready()

    def checkpoint(self):
        self._send_next_request()
        self._send_request_line("checkpoint")

    def _do_get_info(self):
        time_usage = float(self._get_response_line())
        memory_usage = int(self._get_response_line())
        return SandboxProcessInfo(
            time_usage=time_usage,
            memory_usage=memory_usage,
            error=None,
        )

    def _get_response_line(self):
        self.connection.downward.flush()
        line = self.connection.upward.readline().strip()
        assert line, "no line received from driver"
        logging.debug(f"Read response line: {line}")
        return line

    def _get_response_value(self):
        return int(self._get_response_line())

    def _raise_error(self):
        info = self._do_get_info()
        message = self._get_response_line()
        raise AlgorithmRuntimeError(self.process, message, info)

    def _wait_ready(self):
        logging.debug(f"waiting for response ok")
        any_error = self._get_response_value()
        if any_error:
            self._raise_error()

    def _accept_callbacks(self, callback_list):
        while True:
            response = self._get_response_value()
            if response == 1:  # has callback
                logging.debug(f"has callback")
                index = self._get_response_value()
                callback = callback_list[index]
                args = [
                    int(self._get_response_value())
                    for _ in range(callback.__code__.co_argcount)
                ]
                return_value = callback(*args)
                logging.debug(f"callback {index} ({args}) -> {return_value}")
                self.callback_return(return_value)
            elif response == 0:  # no callbacks
                break
            else:  # error
                self._raise_error()

    def _call_lines(self, request):
        yield "call"
        yield request.method_name
        yield len(request.arguments)
        for a in request.arguments:
            yield from serialize_data(a)
        yield int(request.has_return_value)
        yield len(request.callbacks)
        for c in request.callbacks:
            yield c.__code__.co_argcount

    def _send_next_request(self):
        self._wait_ready()
        self._send_request_line("request")

    def _send_request_line(self, line):
        logging.debug(f"sending request downward to driver: {line}")
        print(line, file=self.connection.downward)
