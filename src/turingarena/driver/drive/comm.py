import logging
import threading
from collections import namedtuple
from contextlib import contextmanager

from turingarena.driver.client.commands import DriverState, deserialize_data, serialize_data
from turingarena.driver.drive.context import ExecutionContext
from turingarena.driver.drive.requests import CallRequestSignature, RequestSignature

UPWARD_TIMEOUT = 3.0


SandboxTee = namedtuple("SandboxTee", ["upward_tee", "downward_tee"])


class CommunicationError(Exception):
    """
    Raised when the communication with a process is interrupted.
    """


class InterfaceExitReached(Exception):
    pass


class DriverStop(Exception):
    pass


class ExecutionCommunicator(ExecutionContext):
    def send_driver_state(self, state):
        self.send_driver_upward(state.value)

    def send_driver_upward(self, item):
        if isinstance(item, bool):
            item = int(item)
        print(item, file=self.driver_connection.upward)

    def receive_driver_downward(self):
        self.driver_connection.upward.flush()
        return self.driver_connection.downward.readline().strip()

    def report_ready(self):
        self.send_resource_usage_upward()
        self.send_driver_state(DriverState.READY)

    def next_request(self):
        command = self.receive_driver_downward()
        if command == "stop":
            raise DriverStop
        if command == "call":
            method_name = self.receive_driver_downward()
            return CallRequestSignature(command, method_name)
        else:
            return RequestSignature(command)

    def send_resource_usage_upward(self):
        info = self.process.get_status()
        self.send_driver_state(DriverState.RESOURCE_USAGE)
        self.send_driver_upward(info.time_usage)
        self.send_driver_upward(info.peak_memory_usage)
        self.send_driver_upward(info.current_memory_usage)
        return info

    def _on_timeout(self):
        try:
            logging.info(f"process communication timeout expired")
            self.process.get_status(kill_reason="timeout expired")
        except:
            logging.exception(f"exception while killing for timeout")

    @contextmanager
    def _check_downward_pipe(self):
        try:
            yield
        except BrokenPipeError as e:
            raise CommunicationError(f"downward pipe broken") from e

    def send_downward(self, values):
        with self._check_downward_pipe():
            print(*values, file=self.sandbox_connection.downward)
        print(*values, file=self.sandbox_tee.downward_tee)

    def receive_upward(self):
        with self._check_downward_pipe():
            self.sandbox_connection.downward.flush()

        timer = threading.Timer(UPWARD_TIMEOUT, self._on_timeout)
        timer.start()

        max_line_size = 256

        line = self.sandbox_connection.upward.readline(max_line_size)
        if not line[-1] == "\n":
            raise CommunicationError(f"line sent by process is too long '{line:50}'...")

        line = line.strip()

        timer.cancel()
        timer.join()

        if not line:
            raise CommunicationError(f"process stopped sending data")

        data = tuple(map(int, line.split()))

        print(*data, file=self.sandbox_tee.upward_tee)

        try:
            return data
        except ValueError as e:
            raise CommunicationError(f"process sent invalid data '{line:50}'") from e

    def deserialize_request_data(self):
        deserializer = deserialize_data()
        next(deserializer)
        lines_it = iter(self.receive_driver_downward, None)
        try:
            for line in lines_it:
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
