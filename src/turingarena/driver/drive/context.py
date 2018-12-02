from collections import namedtuple


class ExecutionContext(namedtuple("Executor", [
    "bindings",
    "phase",
    "process",
    "request_lookahead",
    "driver_connection",
    "sandbox_connection",
])):
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


class ExecutionResult(namedtuple("ExecutionResult", [
    "assignments",
    "request_lookahead",
    "does_break",
])):
    def merge(self, other):
        if other is None:
            return self

        return ExecutionResult(
            self.assignments + other.assignments,
            request_lookahead=other.request_lookahead,
            does_break=other.does_break,
        )

    def with_request_processed(self):
        return self._replace(request_lookahead=None)