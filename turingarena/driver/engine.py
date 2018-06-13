import logging
from collections import namedtuple
from enum import Enum

from turingarena.driver.commands import serialize_data

CallRequest = namedtuple("CallRequest", ["method_name", "arguments", "has_return_value", "callbacks"])

DriverClientPhase = Enum("DriverClientPhase", ["PRISTINE", "DOWNWARD", "UPWARD"])


class DriverClientEngine:
    __slots__ = ["connection", "phase"]

    def __init__(self, connection):
        self.connection = connection
        self.phase = DriverClientPhase.PRISTINE

    def call(self, request):
        if self.phase is DriverClientPhase.PRISTINE:
            self.phase = DriverClientPhase.DOWNWARD

        if self.phase is DriverClientPhase.UPWARD:
            upward_request = self.get_response_line()
            if upward_request:
                pass
                # TODO: send the request somewhere to check it is the one expected
            else:
                logging.debug("flush")
                self.phase = DriverClientPhase.DOWNWARD

        if self.phase is DriverClientPhase.DOWNWARD:
            logging.debug("sending call")
            for line in self.call_lines(request):
                self.send_request(line)

        if request.callbacks:
            self.accept_callbacks(request.callbacks)

        if request.has_return_value:
            self.flush_downward()
            logging.debug(f"Receiving return value...")
            return self.get_response_line()
        else:
            return None

    def check_flush_needed(self):
        assert self.phase is DriverClientPhase.UPWARD
        if self.get_response_line():
            self.phase = DriverClientPhase.PRISTINE

    def flush_downward(self):
        if self.phase is DriverClientPhase.DOWNWARD:
            self.connection.downward.flush()
            self.phase = DriverClientPhase.UPWARD

    def get_response_line(self):
        self.connection.downward.flush()
        line = self.connection.upward.readline().strip()
        assert line
        logging.debug(f"Read response line: {line}")
        return int(line)

    def accept_callbacks(self, callback_list):
        while True:
            self.flush_downward()
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
        request = ["callback_return"]
        if return_value is not None:
            request += [1, return_value]
        else:
            request += [0]
        return self.send_request(request)

    def send_exit(self):
        return self.send_request("exit")

    def send_request(self, line):
        logging.debug(f"sending request line: {line}")
        print(line, file=self.connection.downward)
