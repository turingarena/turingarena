import logging
from enum import Enum

from turingarena import InterfaceError
from turingarena.driver.common.description import TreeDumper
from turingarena.driver.compile.analysis import ReferenceResolution
from turingarena.driver.drive.comm import ExecutionCommunicator, CommunicationError, InterfaceExitReached
from turingarena.driver.drive.preprocess import ExecutionPreprocessor
from turingarena.driver.drive.analysis import ReferenceDirection
from turingarena.util.visitor import visitormethod

logger = logging.getLogger(__name__)


class ExecutionPhase(Enum):
    UPWARD = 1
    REQUEST = 2
    DOWNWARD = 3


class NotResolved(Exception):
    """Expression evaluation failed because some values are not resolved"""


class Executor(ExecutionCommunicator, ExecutionPreprocessor):
    __slots__ = []

    @visitormethod
    def evaluate(self, e):
        pass

    def evaluate_IntLiteral(self, e):
        return e.value

    def evaluate_Variable(self, e):
        try:
            return self.bindings[e]
        except KeyError:
            raise NotResolved from None

    def evaluate_Subscript(self, e):
        try:
            return self.bindings[e]
        except KeyError:
            try:
                return self.evaluate(e.array)[self.evaluate(e.index)]
            except KeyError:
                raise NotResolved from None

    def execute(self, n):
        logging.debug(
            f"EXECUTE: {n.__class__.__name__} "
            f"phase: {self.phase} "
            f"request LA: {self.request_lookahead}"
        )

        return self._on_execute(n)

    @visitormethod
    def _on_execute(self, n):
        pass

    def _on_execute_Interface(self, n):
        main = self.transform(n.main)

        logging.debug(f"transformed main block: {TreeDumper().dump(main)}")

        self.with_assigments({
            c.variable: self.evaluate(c.value)
            for c in n.constants
        }).execute(main)

    def _on_execute_Block(self, n):
        result = self.result()
        for n in n.children:
            result = result.merge(self.extend(result).execute(n))
        return result

    def _on_execute_Step(self, n):
        if self.phase is not None:
            return self.execute(n.body)
        else:
            result = self.result()
            for phase in ExecutionPhase:
                direction = n.direction

                if phase == ExecutionPhase.UPWARD and direction != ReferenceDirection.UPWARD:
                    continue

                logging.debug(f"about to run step phase {phase} (prev result: {result})")

                result = result.merge(self.extend(result)._replace(
                    phase=phase,
                ).execute(n.body))

                logging.debug(f"step phase {phase} result: {result}")

            return result

    def _on_execute_Checkpoint(self, n):
        values = self.receive_upward()
        if values != (0,):
            raise CommunicationError(f"expecting checkpoint, got {values}")

        command = self.request_lookahead.command
        if not command == "checkpoint":
            raise InterfaceError(f"expecting 'checkpoint', got '{command}'")
        self.report_ready()
        return self.result().with_request_processed()



    def _on_execute_Callback(self, n):
        assert self.phase is None
        self.report_ready()
        self.send_driver_upward(1)  # has callbacks
        self.send_driver_upward(n.index)
        self.execute(n.body)

    def _on_execute_For(self, n):
        if self.phase is None:
            assert self.request_lookahead is None

        try:
            for_range = self.evaluate(n.index.range)
        except NotResolved:
            # we assume that if the range is not resolved, then the cycle should be skipped
            # FIXME: determine this situation statically
            logger.debug(f"skipping for (phase: {self.phase})")
            return

        results_by_iteration = [
            self.with_assigments(
                [(n.index.variable, i)]
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

    def _on_execute_Loop(self, n):
        context = self
        while True:
            result = context.execute(n.body)
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
            return self.execute(n.branches.then_body)
        else:
            if n.branches.else_body is not None:
                return self.execute(n.branches.else_body)

    def _on_execute_Switch(self, n):
        value = self.evaluate(n.value)

        for c in n.cases:
            for label in c.labels:
                if value == label.value:
                    return self.execute(c.body)

        raise InterfaceError(f"no case matches in switch")

    def _on_execute_object(self, n):
        if self.phase is not None:
            return getattr(self, f"_on_{self.phase.name.lower()}")(n)

    @visitormethod
    def _on_upward(self, n):
        pass

    def _on_upward_object(self, n):
        pass

    def _on_upward_Write(self, n):
        values = self.receive_upward()
        assignments = [
            (a, value)
            for a, value in zip(n.arguments, values)
        ]

        return self.result()._replace(assignments=assignments)

    @visitormethod
    def _on_request(self, n):
        pass

    def _on_request_object(self, n):
        pass

    def _on_request_RequestLookahead(self, n):
        if self.request_lookahead is not None:
            return
        lookahead = self.next_request()
        return self.result()._replace(
            request_lookahead=lookahead,
        )

    def _on_request_CallbackStart(self, n):
        for p in n.prototype.parameters:
            value = self.bindings[p.variable]
            self.send_driver_upward(value)

    def _on_request_Return(self, n):
        has_return_value = self._expect_callback_return()

        if not has_return_value:
            raise InterfaceError(
                f"callback is a function, "
                f"but the provided implementation did not return anything"
            )

        value = int(self.receive_driver_downward())
        return self.result()._replace(assignments=[(n.value, value)])

    def _on_request_CallbackEnd(self, n):
        has_return_value = self._expect_callback_return()
        if has_return_value:
            raise InterfaceError(
                f"callback is a procedure, "
                f"but the provided implementation returned something"
            )

    def _expect_callback_return(self):
        request = self.request_lookahead
        command = request.command
        if not command == "callback_return":
            raise InterfaceError(f"expecting 'callback_return', got '{command}'")
        has_return_value = bool(int(self.receive_driver_downward()))
        return has_return_value

    def _on_request_Exit(self, n):
        command = self.request_lookahead.command
        if command != "exit":
            raise InterfaceError(f"Expecting exit, got {command}")
        raise InterfaceExitReached

    def _on_request_ValueResolve(self, n):
        try:
            self.evaluate(n.value)
        except NotResolved:
            assert self.request_lookahead is not None
            map = dict(n.map)
            try:
                value = map[self.request_lookahead]
            except KeyError:
                value = map[None]  # default
            return self.result()._replace(
                assignments=[(n.value, value)]
            )

    def _on_request_CallArgumentsResolve(self, n):
        command = self.request_lookahead.command
        if not command == "call":
            raise InterfaceError(f"expected call to '{n.method.name}', got {command}")

        method_name = self.request_lookahead.method_name
        if not method_name == n.method.name:
            raise InterfaceError(f"expected call to '{n.method.name}', got call to '{method_name}'")

        parameter_count = int(self.receive_driver_downward())
        if parameter_count != len(n.method.parameters):
            raise InterfaceError(
                f"'{n.method.name}' expects {len(n.method.parameters)} arguments, "
                f"got {parameter_count}"
            )

        assignments = [
            (a, self.deserialize_request_data())
            for a in n.arguments
        ]

        actual_has_return_value = bool(int(self.receive_driver_downward()))
        expected_has_return_value = n.method.has_return_value
        if not actual_has_return_value == expected_has_return_value:
            names = ["procedure", "function"]
            raise InterfaceError(
                f"'{n.method.name}' is a {names[expected_has_return_value]}, "
                f"got call to {names[actual_has_return_value]}"
            )

        callback_count = int(self.receive_driver_downward())
        expected_callback_count = len(n.method.callbacks)
        if not callback_count == expected_callback_count:
            raise InterfaceError(
                f"'{n.method.name}' has a {expected_callback_count} callbacks, "
                f"got {callback_count}"
            )

        for c in n.method.callbacks:
            parameter_count = int(self.receive_driver_downward())
            expected_parameter_count = len(c.parameters)
            if not parameter_count == expected_parameter_count:
                raise InterfaceError(
                    f"'{c.name}' has {expected_parameter_count} parameters, "
                    f"got {parameter_count}"
                )

        return self.result().with_request_processed()._replace(
            assignments=assignments,
        )

    def _on_request_CallReturn(self, n):
        return_value = self.evaluate(n.return_value)

        self.report_ready()
        self.send_driver_upward(return_value)

    def _on_request_CallCompleted(self, n):
        self.report_ready()
        self.send_driver_upward(0)  # no more callbacks

    def _on_execute_AcceptCallbacks(self, n):
        while True:
            [has_callback, callback_index] = self.receive_upward()
            if has_callback:
                callback = n.callbacks[callback_index]
                self.execute(callback)
            else:
                break

    @visitormethod
    def _on_downward(self, n):
        pass

    def _on_downward_object(self, n):
        pass

    def _on_downward_Read(self, n):
        self.send_downward([
            self.evaluate(a)
            for a in n.arguments
        ])
