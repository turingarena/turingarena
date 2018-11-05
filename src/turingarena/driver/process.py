import logging
from collections.__init__ import namedtuple
from contextlib import contextmanager

from turingarena import AlgorithmRuntimeError
from turingarena.driver.commands import DriverState, serialize_data
from turingarena.driver.exceptions import AlgorithmError, TimeLimitExceeded
from turingarena.driver.processinfo import SandboxProcessInfo
from turingarena.driver.proxy import MethodProxy


class ProcessSection:
    @contextmanager
    def _run(self, process, *, time_limit=None):
        self.info_before = process._latest_resource_usage
        yield self
        self.info_after = process._latest_resource_usage

        if time_limit is not None and self.time_usage > time_limit:
            raise TimeLimitExceeded(
                self,
                f"Time limit exceeded: {self.time_usage} > {time_limit}",
            )

    @property
    def time_usage(self):
        return self.info_after.time_usage - self.info_before.time_usage


class Process(ProcessSection):
    def __init__(self, connection):
        self._connection = connection

        self.procedures = MethodProxy(self, has_return_value=False)
        self.functions = MethodProxy(self, has_return_value=True)

        self._latest_resource_usage = None

    def section(self, **kwargs):
        section = ProcessSection()
        return section._run(self, **kwargs)

    def call(self, method_name, *args, has_return_value, callbacks=None):
        if callbacks is None:
            callbacks = {}

        request = CallRequest(
            method_name=method_name,
            arguments=args,
            has_return_value=has_return_value,
            callbacks=callbacks,
        )
        return self._do_call(request)

    def check(self, condition, message, exc_type=AlgorithmError):
        if not condition:
            self.fail(message, exc_type)

    def fail(self, message, exc_type=AlgorithmError):
        raise exc_type(self, message)

    @contextmanager
    def run(self, **kwargs):
        self._wait_ready()
        assert self._latest_resource_usage is not None
        with self._run(self, **kwargs) as section:
            yield section

    def _on_resource_usage(self):
        time_usage = float(self._get_response_line())
        memory_usage = int(self._get_response_line())

        resource_usage = SandboxProcessInfo(
            time_usage=time_usage,
            memory_usage=memory_usage,
            error=None,
        )
        logging.debug(f"got resource usage: {resource_usage}")
        self._latest_resource_usage = resource_usage

    def _do_call(self, request):
        for line in self._call_lines(request):
            self._send_request_line(line)

        self._accept_callbacks(request.callbacks)

        if request.has_return_value:
            self._wait_ready()
            logging.debug(f"Receiving return value...")
            return self._get_response_value()
        else:
            return None

    def exit(self):
        self._send_request_line("exit")

    def stop(self):
        self._send_request_line("stop")
        self._wait_ready()

    def checkpoint(self):
        self._send_request_line("checkpoint")
        self._wait_ready()

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
                self._on_callback_return(return_value)
            elif response == 0:  # no callbacks
                break
            else:  # error
                self._raise_error()

    def _on_callback_return(self, return_value):
        self._send_request_line("callback_return")
        if return_value is not None:
            self._send_request_line(1)
            self._send_request_line(int(return_value))
        else:
            self._send_request_line(0)

    def _get_response_line(self):
        self._connection.downward.flush()
        logging.debug(f"receiving upward from driver...")
        line = self._connection.upward.readline().strip()
        assert line, "no line received from driver"
        logging.debug(f"Read response line: {line}")
        return line

    def _get_response_value(self):
        return int(self._get_response_line())

    def _raise_error(self):
        message = self._get_response_line()
        raise AlgorithmRuntimeError(self, message)

    def _wait_ready(self):
        logging.debug(f"waiting for response ok")
        while True:
            state = DriverState(self._get_response_value())
            if state is DriverState.READY:
                break
            if state is DriverState.RESOURCE_USAGE:
                self._on_resource_usage()
            if state is DriverState.ERROR:
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

    def _send_request_line(self, line):
        logging.debug(f"sending request downward to driver: {line}")
        print(line, file=self._connection.downward)


CallRequest = namedtuple("CallRequest", ["method_name", "arguments", "has_return_value", "callbacks"])
