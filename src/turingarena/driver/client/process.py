import logging
import math
from collections import namedtuple
from contextlib import contextmanager

from turingarena.driver.client.commands import DriverState, serialize_data
from turingarena.driver.client.exceptions import *
from turingarena.driver.client.processinfo import SandboxProcessInfo
from turingarena.driver.client.proxy import MethodProxy


class ProcessSection:
    def __init__(self):
        self._time_usage = None
        self._peak_memory_usage = 0

    @property
    def time_usage(self):
        return self._time_usage

    @property
    def peak_memory_usage(self):
        return self._peak_memory_usage


class Process:
    def __init__(self, connection):
        self._connection = connection

        self.procedures = MethodProxy(self, has_return_value=False)
        self.functions = MethodProxy(self, has_return_value=True)

        self._latest_resource_usage = None

        self._main_section = ProcessSection()
        self._running_sections = set()

    @contextmanager
    def section(self, time_limit=None, memory_limit=None):
        if time_limit is None:
            time_limit = math.inf
        if memory_limit is None:
            memory_limit = math.inf

        section = ProcessSection()

        self._running_sections.add(section)

        time_usage_before = self._latest_resource_usage.time_usage
        try:
            yield section
        finally:
            self._running_sections.remove(section)
        time_usage_after = self._latest_resource_usage.time_usage

        section._time_usage = time_usage_after - time_usage_before

        self.check(
            section.time_usage <= time_limit,
            f"time usage: {section.time_usage:.6f}s > {time_limit:.6f}s",
            exc_type=TimeLimitExceeded,
        )

        self.check(
            section.peak_memory_usage <= memory_limit,
            f"peak memory usage: {section.peak_memory_usage / 1024} kB > {memory_limit / 1024} kB",
            exc_type=MemoryLimitExceeded,
        )

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

    def check(self, condition, message, exc_type=AlgorithmLogicError):
        if not condition:
            self.fail(message, exc_type)

    def fail(self, message, exc_type=AlgorithmLogicError):
        raise exc_type(message, process=self)

    @contextmanager
    def _run(self, **kwargs):
        self.checkpoint()
        assert self._latest_resource_usage is not None
        with self.section(**kwargs) as main_section:
            self._main_section = main_section
            try:
                yield self
                self._send_exit()
                self.stop()
            except InterfaceExit:
                self._send_exit()
                self.stop()
                raise

    @property
    def current_memory_usage(self):
        return self._latest_resource_usage.current_memory_usage

    @property
    def peak_memory_usage(self):
        return self._main_section.peak_memory_usage

    @property
    def time_usage(self):
        return self._main_section.time_usage

    def limit_memory(self, memory_limit):
        self.check(
            self.current_memory_usage <= memory_limit,
            f"current memory usage: {self.current_memory_usage / 1024} kB > {memory_limit / 1024} kB",
            exc_type=MemoryLimitExceeded,
        )

    def _on_resource_usage(self):
        time_usage = float(self._get_response_line())
        peak_memory_usage = int(self._get_response_line())
        current_memory_usage = int(self._get_response_line())

        resource_usage = SandboxProcessInfo(
            time_usage=time_usage,
            peak_memory_usage=peak_memory_usage,
            current_memory_usage=current_memory_usage,
            error=None,
        )

        logging.debug(f"got resource usage: {resource_usage}")

        self._latest_resource_usage = resource_usage

        for section in self._running_sections:
            section._peak_memory_usage = max(
                section._peak_memory_usage,
                resource_usage.peak_memory_usage
            )

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
        raise InterfaceExit

    def stop(self):
        self._send_request_line("stop")
        self._wait_ready()

    def checkpoint(self):
        self._send_request_line("checkpoint")
        self._wait_ready()

    def _send_exit(self):
        self._send_request_line("exit")

    def _accept_callbacks(self, callback_list):
        while True:
            self._wait_ready()
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
        self.fail(message, exc_type=AlgorithmRuntimeError)

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
