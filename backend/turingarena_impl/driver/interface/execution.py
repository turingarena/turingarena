import logging
from collections import namedtuple
from typing import List, Tuple, Any

from turingarena.driver.commands import deserialize_data, serialize_data
from turingarena_impl.driver.interface.exceptions import CommunicationBroken
from turingarena_impl.driver.interface.nodes import ExecutionResult
from turingarena_impl.driver.interface.variables import Reference, ReferenceDirection, ReferenceStatus

logger = logging.getLogger(__name__)

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
        logging.debug(f"receive_driver_downward...")
        line = self.driver_connection.downward.readline().strip()
        logging.debug(f"receive_driver_downward -> {line}")
        return line

    def next_request(self):
        while True:
            command = self.receive_driver_downward()
            if command == "wait":
                wait = int(self.receive_driver_downward())
                info = self.process.get_status(wait=wait)
                self.send_driver_upward(info.time_usage)
                self.send_driver_upward(info.memory_usage)
                self.send_driver_upward(info.error)
            else:
                assert command == "request"
                break
        command = self.receive_driver_downward()
        if command == "call":
            method_name = self.receive_driver_downward()
            return CallRequestSignature(command, method_name)
        else:
            return RequestSignature(command)

    def send_downward(self, values):
        try:
            logger.debug(f"send_downward: {values}")
            print(*values, file=self.sandbox_connection.downward)
        except BrokenPipeError:
            raise CommunicationBroken

    def receive_upward(self):
        try:
            self.sandbox_connection.downward.flush()
        except BrokenPipeError:
            raise CommunicationBroken

        logger.debug(f"receive_upward...")
        line = self.sandbox_connection.upward.readline().strip()
        logger.debug(f"receive_upward -> {line}")
        if not line:
            raise CommunicationBroken

        return tuple(map(int, line.split()))

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

    @property
    def is_first_execution(self):
        return (
                self.direction is ReferenceDirection.UPWARD
                and self.phase is ReferenceStatus.DECLARED
                or self.direction is not ReferenceDirection.UPWARD
                and self.phase is ReferenceStatus.RESOLVED
        )

    def result(self):
        return ExecutionResult(
            assignments=[],
            request_lookahead=self.request_lookahead,
            does_break=False,
        )
