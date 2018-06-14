import logging
from collections import namedtuple

from turingarena.driver.commands import serialize_data

CallRequest = namedtuple("CallRequest", ["method_name", "arguments", "has_return_value", "callbacks"])


class DriverClientEngine:
    __slots__ = ["connection", "phase"]

    def __init__(self, connection):
        self.connection = connection

    def call(self, request):
        for line in self.call_lines(request):
            self.send_request(line)

        if request.callbacks:
            self.accept_callbacks(request.callbacks)

        if request.has_return_value:
            logging.debug(f"Receiving return value...")
            return self.get_response_line()
        else:
            return None

    def get_response_line(self):
        self.connection.downward.flush()
        line = self.connection.upward.readline().strip()
        assert line
        logging.debug(f"Read response line: {line}")
        return int(line)

    def accept_callbacks(self, callback_list):
        while True:
            if self.get_response_line():  # has callback
                logging.debug(f"has callback")
                index = self.get_response_line()
                callback = callback_list[index]
                args = [
                    int(self.get_response_line())
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
        self.send_request("callback_return")
        if return_value is not None:
            self.send_request(1)
            self.send_request(int(return_value))
        else:
            self.send_request(0)

    def send_exit(self):
        return self.send_request("exit")

    def send_request(self, line):
        logging.debug(f"sending request line: {line}")
        print(line, file=self.connection.downward)
