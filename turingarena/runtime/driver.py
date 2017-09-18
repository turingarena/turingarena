from collections import deque
from functools import partial

from turingarena.runtime.data import Variable


class Globals:
    pass


class BaseDriverEngine:
    phases = [
        "global_data",
        "upward_data",
        "upward_control",
        "downward_control",
        "downward_data",
    ]

    def __init__(
            self,
            upward_pipe,
            downward_pipe,
    ):

        self.locals = {
            phase: deque()
            for phase in self.phases
        }

        self.globals = Globals()
        self.global_data(
            var=partial(self.next_variable, "global_data"),
            globals=self.globals,
        )

        self.upward_data = self.upward_data(
            var=partial(self.next_variable, "upward_data"),
            pipe=upward_pipe,
        )
        self.upward_control = self.upward_control(
            var=partial(self.next_variable, "upward_control"),
        )
        self.downward_control = self.downward_control(
            var=partial(self.next_variable, "downward_control"),
        )
        self.downward_data = self.downward_data(
            var=partial(self.next_variable, "downward_data"),
            pipe=downward_pipe,
        )

        self.callbacks = {}

        # prepare downward_control to receive data
        next(self.downward_control)

    def next_variable(self, phase, t):
        queue = self.locals[phase]
        if len(queue) == 0:
            local = Variable(t)
            for p in self.locals.keys():
                self.locals[p].append(local)
        return queue.popleft()

    def start(self):
        next(self.upward_data)
        command, *command_args = next(self.upward_control)
        assert command == "start" and len(command_args) == 0

    def stop(self):
        self.downward_control.send(("stop",))
        next(self.downward_data)

    def invoke_callback(self, name, args):
        return self.callbacks[name](*args)

    def call(self, name, *call_args):
        self.downward_control.send(("call", name, call_args))
        while True:
            next(self.downward_data)

            # extra trip for callback detection
            next(self.upward_data)
            next(self.upward_control)
            next(self.downward_control)
            next(self.downward_data)

            next(self.upward_data)
            command, *command_args = next(self.upward_control)

            if command == "callback":
                return_value = self.invoke_callback(*command_args)
                self.downward_control.send(("return", return_value))
            elif command == "call_return":
                function_name, return_value = command_args
                assert function_name == name
                return return_value
            else:
                raise ValueError


class BaseDriver:
    def __init__(self, process):
        self._engine = self._engine_class(
            downward_pipe=process.downward_pipe,
            upward_pipe=process.upward_pipe,
        )

    def __enter__(self):
        self._engine.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._engine.stop()


def expect_call(command, expected_name):
    command_type, *command_args = command
    if command_type != "call":
        raise ValueError("unexpected call, expecting {cmd}".format(cmd=command))
    name, call_args = command_args
    if name != expected_name:
        raise ValueError("unexpected call to {actual}, expecting {expected}".format(
            actual=name,
            expected=expected_name,
        ))
    return call_args


def expect_return(command):
    command_type, *command_args = command
    if command_type != "return":
        raise ValueError("expecting return, received {cmd}".format(cmd=command))
    return_value, = command_args
    return return_value


def expect_stop(command):
    command_type, *command_args = command
    if command_type != "stop":
        raise ValueError("expecting stop, received {cmd}".format(cmd=command))


def read(types, *, file):
    raw_values = file.readline().strip().split()
    return [t(value) for value, t in zip(raw_values, types)]


def lazy_yield():
    """
    Returns a generator that yields exactly once.

    Used in combination with the 'yield from' construct
    to implement the lazy yield mechanism used in upward data protocol.
    """
    return iter([None])
