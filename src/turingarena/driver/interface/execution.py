import logging
import threading
from collections import namedtuple
from contextlib import contextmanager
from typing import List, Tuple, Any

from turingarena import InterfaceError
from turingarena.driver.client.commands import deserialize_data, serialize_data, DriverState
from turingarena.driver.interface.analysis import TreeAnalyzer
from turingarena.driver.interface.exceptions import CommunicationError, DriverStop, InterfaceExitReached
from turingarena.driver.interface.nodes import ExecutionResult
from turingarena.driver.interface.phase import ExecutionPhase
from turingarena.driver.interface.requests import RequestSignature, CallRequestSignature
from turingarena.driver.interface.statements.call import CallArgumentsResolve
from turingarena.driver.interface.statements.callback import CallbackEnd, Return, Exit
from turingarena.driver.interface.statements.if_else import IfConditionResolve
from turingarena.driver.interface.statements.io import Checkpoint
from turingarena.driver.interface.statements.switch import SwitchValueResolve
from turingarena.driver.interface.variables import Reference, ReferenceDirection, ReferenceResolution
from turingarena.util.visitor import visitormethod

logger = logging.getLogger(__name__)

UPWARD_TIMEOUT = 3.0

Assignments = List[Tuple[Reference, Any]]


class NodeExecutionContext(namedtuple("NodeExecutionContext", [
    "bindings",
    "direction",
    "phase",
    "process",
    "request_lookahead",
    "driver_connection",
    "sandbox_connection",
]), TreeAnalyzer):
    __slots__ = []

    def send_driver_state(self, state):
        self.send_driver_upward(state.value)

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

        timer.cancel()
        timer.join()

        if not line:
            raise CommunicationError(f"stopped sending data")

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

    @visitormethod
    def evaluate(self, e):
        pass

    def evaluate_IntLiteral(self, e):
        return e.value

    def evaluate_VariableReference(self, e):
        return self.bindings[self.reference(e)]

    def evaluate_Subscript(self, e):
        try:
            return self.bindings[self.reference(e)]
        except KeyError:
            return self.evaluate(e.array)[self.evaluate(e.index)]

    def _needs_request_lookahead(self, n):
        types = [
            Checkpoint,
            SwitchValueResolve,
            IfConditionResolve,
            CallbackEnd,
            Return,
            CallArgumentsResolve,
            Exit,
        ]

        return any(isinstance(n, t) for t in types)

    def execute(self, n):
        context = self

        logging.debug(
            f"EXECUTE: {n} "
            f"phase: {self.phase} "
            f"request LA: {self.request_lookahead}"
        )

        should_lookahead_request = (
                context.request_lookahead is None
                and self._needs_request_lookahead(n)
                and context.phase is ExecutionPhase.REQUEST
        )

        result = context.result()
        if should_lookahead_request:
            lookahead = context.next_request()
            result = result._replace(
                request_lookahead=lookahead,
            )
            context = context.extend(result)

        return context._on_execute(n)

    @visitormethod
    def _on_execute(self, n):
        pass

    def _on_execute_InterfaceDefinition(self, n):
        description = "\n".join(n.main_block.node_description)
        # logger.debug(f"Description: {description}")

        self.with_assigments({
            c.variable.as_reference(): self.evaluate(c.value)
            for c in n.constants
        }).execute(n.main_block)

    def _on_execute_Block(self, n):
        return self._execute_sequence(n.children)

    def _on_execute_Step(self, n):
        assert n.children

        if self.phase is not None:
            return self._execute_sequence(n.children)
        else:
            result = self.result()
            for phase in ExecutionPhase:
                direction = n.direction

                if phase == ExecutionPhase.UPWARD and direction != ReferenceDirection.UPWARD:
                    continue

                result = result.merge(self.extend(result)._replace(
                    phase=phase,
                )._execute_sequence(n.children))

            return result

    def _execute_sequence(self, nodes):
        result = self.result()
        for n in nodes:
            result = result.merge(self.extend(result).execute(n))
        return result

    def _on_execute_Read(self, n):
        if self.phase is ExecutionPhase.DOWNWARD:
            logging.debug(f"Bindings: {self.bindings}")
            self.send_downward([
                self.evaluate(a)
                for a in n.arguments
            ])

    def _on_execute_Write(self, n):
        if self.phase is ExecutionPhase.UPWARD:
            values = self.receive_upward()
            assignments = [
                (self.reference(a), value)
                for a, value in zip(n.arguments, values)
            ]

            return self.result()._replace(assignments=assignments)

    def _on_execute_Checkpoint(self, n):
        if self.phase is ExecutionPhase.UPWARD:
            values = self.receive_upward()
            if values != (0,):
                raise CommunicationError(f"expecting checkpoint, got {values}")
        if self.phase is ExecutionPhase.REQUEST:
            command = self.request_lookahead.command
            if not command == "checkpoint":
                raise InterfaceError(f"expecting 'checkpoint', got '{command}'")
            self.report_ready()
            return self.result().with_request_processed()

    def _on_execute_Switch(self, n):
        value = self.evaluate(n.value)

        for c in n.cases:
            for label in c.labels:
                if value == label.value:
                    return self.execute(c.body)

        raise InterfaceError(f"no case matches in switch")

    def _on_execute_SwitchValueResolve(self, n):
        if self.phase is ExecutionPhase.REQUEST:
            matching_cases = self._find_matching_cases(n, self.request_lookahead)
            [case] = matching_cases
            [label] = case.labels
            assignments = [(self.reference(n.value), label.value)]

            return self.result()._replace(assignments=assignments)

    def _find_matching_cases(self, n, request):
        matching_cases_requests = list(self._find_cases_expecting(n, request))
        if matching_cases_requests:
            return matching_cases_requests
        else:
            return list(self._find_cases_expecting(n, None))

    def _find_cases_expecting(self, n, request):
        for c in n.cases:
            if request in self.first_requests(c.body):
                yield c

    def _on_execute_CallbackImplementation(self, n):
        assert self.phase is None
        self.report_ready()
        self.send_driver_upward(1)  # has callbacks
        self.send_driver_upward(n.index)
        self.execute(n.body)

    def _on_execute_CallbackStart(self, n):
        if self.phase is ExecutionPhase.REQUEST:
            for p in n.prototype.parameters:
                r = p.as_reference()
                value = self.bindings[r]
                self.send_driver_upward(value)

    def _on_execute_Return(self, n):
        if self.phase is ExecutionPhase.REQUEST:
            has_return_value = self._expect_callback_return()

            if not has_return_value:
                raise InterfaceError(
                    f"callback is a function, "
                    f"but the provided implementation did not return anything"
                )

            value = int(self.receive_driver_downward())
            return self.result()._replace(assignments=[(self.reference(n.value), value)])

    def _on_execute_CallbackEnd(self, n):
        if self.phase is ExecutionPhase.REQUEST:
            has_return_value = self._expect_callback_return()
            if has_return_value:
                raise InterfaceError(
                    f"callback is a procedure, "
                    f"but the provided implementation returned something"
                )

    def _on_execute_For(self, n):
        if self.phase is None:
            assert self.request_lookahead is None

        try:
            for_range = self.evaluate(n.index.range)
        except KeyError:
            # we assume that if the range is not resolved, then the cycle should be skipped
            # FIXME: determine this situation statically
            logger.debug(f"skipping for (phase: {self.phase})")
            return

        results_by_iteration = [
            self.with_assigments(
                [(n.index.variable.as_reference(), i)]
            ).execute(n.body)
            for i in range(for_range)
        ]

        assignments = [
            (a.reference, [
                result.assignments[a.reference._replace(
                    indexes=a.reference.indexes + (self.variable(n.index),),
                )]
                for result in results_by_iteration
            ])
            for a in self.reference_actions(n)
            if isinstance(a, ReferenceResolution)
        ]

        return self.result()._replace(assignments=assignments)

    def _expect_callback_return(self):
        request = self.request_lookahead
        command = request.command
        if not command == "callback_return":
            raise InterfaceError(f"expecting 'callback_return', got '{command}'")
        has_return_value = bool(int(self.receive_driver_downward()))
        return has_return_value

    def _on_execute_Exit(self, n):
        if self.phase is ExecutionPhase.REQUEST:
            command = self.request_lookahead.command
            if command != "exit":
                raise InterfaceError(f"Expecting exit, got {command}")
            raise InterfaceExitReached

    def _on_execute_Loop(self, n):
        context = self
        while True:
            result = context.execute(n.body)
            logger.debug(f"request_lookahead: {result.request_lookahead}")
            context = context._replace(
                request_lookahead=result.request_lookahead,
            )
            if result.does_break:
                return result

    def _on_execute_Break(self, n):
        return self.result()._replace(does_break=True)

    def _on_execute_If(self, n):
        condition_value = self.evaluate(n.condition)
        if condition_value:
            return self.execute(n.then_body)
        elif n.else_body is not None:
            return self.execute(n.else_body)

    def _on_execute_IfConditionResolve(self, n):
        if self.phase is ExecutionPhase.REQUEST:
            [condition_value] = self._find_conditions(n, self.request_lookahead)
            return self.result()._replace(
                assignments=[(self.reference(n.condition), condition_value)]
            )

    def _find_conditions(self, n, request):
        matching_conditions = frozenset(self._find_conditions_expecting(n, request))
        if not matching_conditions:
            matching_conditions = frozenset(self._find_conditions_expecting_no_request(n))
        return matching_conditions

    def _find_conditions_expecting(self, n, request):
        if request in self.first_requests(n.then_body):
            yield 1
        if n.else_body is not None:
            if request in self.first_requests(n.else_body):
                yield 0

    def _find_conditions_expecting_no_request(self, n):
        yield from self._find_conditions_expecting(n, None)
        if n.else_body is None:
            yield 0

    def _on_execute_CallArgumentsResolve(self, n):
        if self.phase is not ExecutionPhase.REQUEST:
            return

        method = n.method

        command = self.request_lookahead.command
        if not command == "call":
            raise InterfaceError(f"expected call to '{method.name}', got {command}")

        method_name = self.request_lookahead.method_name
        if not method_name == method.name:
            raise InterfaceError(f"expected call to '{method.name}', got call to '{method_name}'")

        parameter_count = int(self.receive_driver_downward())
        if parameter_count != len(method.parameters):
            raise InterfaceError(
                f"'{method.name}' expects {len(method.parameters)} arguments, "
                f"got {parameter_count}"
            )

        assignments = [
            (self.reference(a), self.deserialize_request_data())
            for a in n.arguments
        ]

        has_return_value = bool(int(self.receive_driver_downward()))
        expects_return_value = (n.return_value is not None)
        if not has_return_value == expects_return_value:
            names = ["procedure", "function"]
            raise InterfaceError(
                f"'{method.name}' is a {names[expects_return_value]}, "
                f"got call to {names[has_return_value]}"
            )

        callback_count = int(self.receive_driver_downward())
        expected_callback_count = len(n.callbacks)
        if not callback_count == expected_callback_count:
            raise InterfaceError(
                f"'{method.name}' has a {expected_callback_count} callbacks, "
                f"got {callback_count}"
            )

        for c in n.callbacks:
            parameter_count = int(self.receive_driver_downward())
            expected_parameter_count = len(c.prototype.parameters)
            if not parameter_count == expected_parameter_count:
                raise InterfaceError(
                    f"'{c.name}' has {expected_parameter_count} parameters, "
                    f"got {parameter_count}"
                )

        return self.result().with_request_processed()._replace(
            assignments=assignments,
        )

    def _on_execute_CallReturn(self, n):
        if self.phase is ExecutionPhase.REQUEST:
            return_value = self.evaluate(n.return_value)
            self.report_ready()
            self.send_driver_upward(return_value)

    def _on_execute_CallCompleted(self, n):
        if self.phase is ExecutionPhase.REQUEST:
            self.report_ready()
            self.send_driver_upward(0)  # no more callbacks

    def _on_execute_AcceptCallbacks(self, n):
        while True:
            [has_callback] = self.receive_upward()
            if has_callback:
                [callback_index] = self.receive_upward()
                callback = n.callbacks[callback_index]
                self.execute(callback)
            else:
                break

    def _on_execute_IntermediateNode(self, n):
        pass
