import logging
import threading
from collections import namedtuple
from contextlib import contextmanager
from typing import List, Tuple, Any

from turingarena.driver.commands import deserialize_data, serialize_data
from turingarena_impl.driver.interface.exceptions import CommunicationError, DriverStop
from turingarena_impl.driver.interface.nodes import ExecutionResult
from turingarena_impl.driver.interface.variables import Reference

logger = logging.getLogger(__name__)

UPWARD_TIMEOUT = 3.0

Assignments = List[Tuple[Reference, Any]]

RequestSignature = namedtuple("RequestSignature", ["command"])
CallRequestSignature = namedtuple("CallRequestSignature", ["command", "method_name"])


class NodeExecutionContext(namedtuple("NodeExecutionContext", [
    "bindings",
    "direction",
    "phase",
    "process",
    "request_lookahead",
    "driver_connection",
    "sandbox_connection",
])):
    __slots__ = []

    def send_driver_upward(self, item):
        logging.debug(f"send_driver_upward: {item}")
        if isinstance(item, bool):
            item = int(item)
        print(item, file=self.driver_connection.upward)

    def receive_driver_downward(self):
        self.driver_connection.upward.flush()
        logging.debug(f"receive_driver_downward...", stack_info=True)
        line = self.driver_connection.downward.readline().strip()
        logging.debug(f"receive_driver_downward -> {line}")
        return line

    def next_request(self):
        self.send_driver_upward(0)  # ok, no errors
        while True:
            command = self.receive_driver_downward()
            if command == "wait":
                kill = int(self.receive_driver_downward())
                if kill:
                    kill_reason = "explicitly requested"
                else:
                    kill_reason = None
                self.perform_wait(kill_reason)
                self.send_driver_upward(0)
            elif command == "stop":
                raise DriverStop
            else:
                assert command == "request"
                break
        command = self.receive_driver_downward()
        if command == "call":
            method_name = self.receive_driver_downward()
            return CallRequestSignature(command, method_name)
        else:
            return RequestSignature(command)

    def perform_wait(self, kill_reason):
        info = self.process.get_status(kill_reason=kill_reason)
        self.send_driver_upward(info.time_usage)
        self.send_driver_upward(info.memory_usage)
        return info

    def _on_timeout(self):
        logging.info(f"process communication timeout expired")
        self.process.get_status(kill_reason="timeout expired")

    @contextmanager
    def _check_downward_pipe(self):
        try:
            yield
        except BrokenPipeError as e:
            raise CommunicationError(f"downward pipe broken") from e

    def send_downward(self, values):
        logger.debug(f"send_downward: {values}")
        with self._check_downward_pipe():
            print(*values, file=self.sandbox_connection.downward)

    def receive_upward(self):
        with self._check_downward_pipe():
            self.sandbox_connection.downward.flush()

        timer = threading.Timer(UPWARD_TIMEOUT, self._on_timeout)
        timer.start()

        logger.debug(f"receive upward from process...")
        line = self.sandbox_connection.upward.readline().strip()
        logger.debug(f"receive upward from process -> {line!r}")

        if not timer.is_alive():
            raise CommunicationError(f"process stopped sending data (timeout: {UPWARD_TIMEOUT}s)")
        timer.cancel()

        if not line:
            raise CommunicationError(f"upward pipe closed")

        try:
            return tuple(map(int, line.split()))
        except ValueError as e:
            raise CommunicationError(f"process sent invalid data") from e

    def deserialize_request_data(self):
        logger.debug(f"deserialize_request_data")
        deserializer = deserialize_data()
        next(deserializer)
        lines_it = iter(self.receive_driver_downward, None)
        try:
            for line in lines_it:
                logger.debug(f"deserializing line {line}...")
                deserializer.send(line)
        except StopIteration as e:
            result = e.value
        else:
            raise ValueError(f"too few lines")
        return result

    def serialize_response_data(self, value):
        lines = serialize_data(value)
        for line in lines:
            self.send_driver_upward(int(line))

    def with_assigments(self, assignments):
        return self._replace(bindings={
            **self.bindings,
            **dict(assignments),
        })

    def extend(self, execution_result):
        return self.with_assigments(execution_result.assignments)._replace(
            request_lookahead=execution_result.request_lookahead,
        )

    def result(self):
        return ExecutionResult(
            assignments=[],
            request_lookahead=self.request_lookahead,
            does_break=False,
        )
