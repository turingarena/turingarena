import logging
from collections import deque
from functools import partial

from turingarena.runtime.data import Variable, ProtocolError

import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.DEBUG, logger=logger)


class UnexpectedCallback(Exception):
    pass


class Globals:
    pass


class BaseDriverEngine:
    phases = [
        "global_data",
        "porcelain",
        "plumbing",
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

        self.expected_callbacks = {
            phase: deque()
            for phase in self.phases
        }

        self.globals = Globals()
        self.global_data(
            var=partial(self.next_variable, "global_data"),
            globals=self.globals,
        )

        self.plumbing = self.plumbing(
            var=partial(self.next_variable, "plumbing"),
            upward_pipe=upward_pipe,
            downward_pipe=downward_pipe,
        )
        self.porcelain = self.porcelain(
            var=partial(self.next_variable, "porcelain"),
            flush=self.on_flush,
        )

        self.downward_pipe = downward_pipe
        self.upward_pipe = upward_pipe

        self.output_sent = False


    def next_variable(self, phase, t):
        queue = self.locals[phase]
        if len(queue) == 0:
            local = Variable(t)
            for p in self.locals.keys():
                self.locals[p].append(local)
        return queue.popleft()

    def send_command(self, command):
        logger.debug("sending command %s", command)
        command, *command_args = self.porcelain.send(command)
        logger.debug("received status %s %s", command, command_args)
        return command, command_args

    def start(self):
        status, status_args = self.send_command(None)
        if status != "main_started":
            raise ProtocolError("unexpected status: " + status)

    def stop(self):
        status, status_args = self.send_command(None)
        if status != "main_stopped":
            raise ProtocolError("unexpected status: " + status)
        self.on_flush()

    def invoke_callback(self, callbacks, name, args):
        key = "callback_{}".format(name)
        if key not in callbacks:
            raise UnexpectedCallback(name)

        return_value = callbacks[key](*args)

        if return_value is not None:
            status, *status_args = self.send_command(("return", return_value))
            if status != "return_accepted":
                raise ProtocolError("unexpected status: " + status)

        self.maybe_advance_plumbing()

        status, *status_args = self.send_command(None)
        if status != "callback_stopped":
            raise ProtocolError("unexpected status: " + status)

    def process_callbacks(self, callbacks):
        while True:
            status, status_args = self.send_command(None)
            if status == "callback_started":
                self.invoke_callback(callbacks, *status_args)
            elif status == "call_returned":
                function_name, return_value = status_args
                return return_value
            else:
                raise ProtocolError("unexpected status: " + status)

    def on_flush(self):
        logger.debug("communication block ended (porcelain flush)")
        if not self.output_sent:
            raise ProtocolError(
                "no output was sent on flush, "
                "make sure you have a 'call' which generates output in each communication block")
        self.output_sent = False

    def call(self, name, *call_args, has_return, **kwargs):
        callbacks = {n: f for n, f in kwargs.items() if n.startswith("callback_")}

        status, status_args = self.send_command(("call", name, call_args))

        if status != "call_accepted":
            raise ProtocolError("unexpected status: " + status)

        has_output = has_return or len(callbacks) > 0
        if has_output:
            self.maybe_advance_plumbing()
        return self.process_callbacks(callbacks)

    def maybe_advance_plumbing(self):
        if not self.output_sent:
            logger.debug("call needs output but input not sent yet, advancing data in pipes...")
            next(self.plumbing)
            logger.debug("data exchanged in pipes.")
        self.output_sent = True


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
        if exc_val is None:
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
