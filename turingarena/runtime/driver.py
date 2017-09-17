from collections import deque
from functools import partial

from turingarena.runtime.data import Variable


class ProtocolEngine:
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
            upward_data,
            upward_control,
            downward_control,
            downward_data,
            global_data,
            main,
            **callbacks
    ):

        self.locals = {
            phase: deque()
            for phase in self.phases
        }

        class Globals:
            pass

        self.globals = Globals()
        global_data(
            var=partial(self.next_local, "global_data"),
            globals=self.globals,
        )

        self.upward_data = upward_data(
            var=partial(self.next_local, "upward_data"),
            pipe=upward_pipe,
        )
        self.upward_control = upward_control(
            var=partial(self.next_local, "upward_control"),
        )
        self.downward_control = downward_control(
            var=partial(self.next_local, "downward_control"),
        )
        self.downward_data = downward_data(
            var=partial(self.next_local, "downward_data"),
            pipe=downward_pipe,
        )

        self.main = main
        self.callbacks = callbacks

        # prepare downward_control to receive data
        next(self.downward_control)

    def next_local(self, phase, t, value=None):
        queue = self.locals[phase]
        if len(queue) == 0:
            local = Variable(t, value)
            for p in self.locals.keys():
                self.locals[p].append(local)
        return queue.popleft()

    def start(self):
        next(self.upward_data)
        command, *command_args = next(self.upward_control)
        assert command == "main" and len(command_args) == 0
        return_value = self.invoke_main()
        self.downward_control.send(("return", return_value))
        next(self.downward_data)

    def invoke_main(self):
        return self.main()

    def invoke_callback(self, name, args):
        return self.callbacks["callback_" + name](*args)

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


class BaseInterface:
    def __init__(self, **kwargs):
        super().__init__()
        self._engine = ProtocolEngine(**kwargs)

    def main(self):
        self._engine.start()


def expect_call(command, expected_name):
    command_type, *command_args = command
    if command_type != "call":
        raise "unexpected call, expecting {cmd}".format(cmd=command)
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
        raise "unexpected return, expecting {cmd}".format(cmd=command)
    return_value, = command_args
    return return_value


def read(types, *, file):
    raw_values = file.readline().strip().split()
    return [t(value) for value, t in zip(raw_values, types)]


"""
Returns a generator that yields exactly once.

Used in combination with the 'yield from' construct
to implement the lazy yield mechanism used in upward data protocol.
"""


def lazy_yield():
    return (_ for _ in (None,))
