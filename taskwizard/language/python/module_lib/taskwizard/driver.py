from abc import abstractmethod
from collections import deque


def get_value(value):
    if value is None: raise ValueError("not set")
    return value


def set_once(old_value, new_value):
    if old_value is not None: raise ValueError("already set")
    return new_value


def is_set(value):
    return value is not None


class BaseInterfaceEngine:

    phases = ["preflight", "downward", "upward", "postflight"]

    def __init__(self, interface, upward_pipe, downward_pipe):
        self.upward_pipe = upward_pipe
        self.downward_pipe = downward_pipe

        self.interface = interface

        self.protocols = {
            phase: self.main(phase)
            for phase in self.phases
        }
        self.locals = {
            phase: deque()
            for phase in self.phases
        }

        self.upward_should_stop_on_input = None

        self.start()

    def get_local(self, phase):
        queue = self.locals[phase]
        if len(queue) == 0:
            local = Local(self)
            for p in self.locals.keys():
                self.locals[p].append(local)
        return queue.popleft()

    def start(self):
        next(self.protocols["preflight"])
        self.upward_should_stop_on_input = True
        next(self.protocols["upward"])

    def call(self, name, *call_args):
        self.protocols["preflight"].send(("call", name, call_args))
        while True:
            next(self.protocols["downward"])
            next(self.protocols["upward"])

            command, *command_args = next(self.protocols["postflight"])

            if command == "callback":
                next(self.protocols["preflight"])
                return_value = self.invoke_callback(*command_args)
                self.protocols["preflight"].send(("callback_return", return_value))
            elif command == "call_return":
                return_value, = command_args
                return return_value
            else: raise ValueError

    def invoke_callback(self, name, args):
        return self.interface._callbacks[name](*args)

    def upward_lazy_yield(self):
        yield from self.upward_maybe_yield()
        self.upward_should_stop_on_input = True

    def upward_maybe_yield(self):
        if self.upward_should_stop_on_input: yield
        self.upward_should_stop_on_input = False

    def expect_call(self, command, expected_name):
        command, *command_args = command
        if command != "call": "unexpected call, expecting {cmd}".format(cmd=command)
        name, call_args = command_args
        if name != expected_name:
            raise ValueError("unexpected call to {actual}, expecting {expected}".format(
                actual=name,
                expected=expected_name,
            ))
        return call_args

    def expect_callback_return(self, command):
        command, *command_args = command
        if command != "callback_return": "unexpected callback return, expecting {cmd}".format(cmd=command)
        return_value, = command_args
        return return_value

    def set_callback(self, name, *args):
        if self.callback is not None: raise ValueError
        self.callback = name
        self.callback_args = args

    def read_upward(self, *types):
        raw_values = self.upward_pipe.readline().strip().split()
        return [t(value) for value, t in zip(raw_values, types)]

    @abstractmethod
    def main(self):
        pass


class BaseStruct:

    def __init__(self):
        self._delegate = {}

        for k, t in self._fields.items():
            if issubclass(t, BaseArray):
                self._delegate[k] = t()
            else:
                self._delegate[k] = None

    def _check_field(self, key):
        # raise if not found
        return self._fields[key]

    def __getattr__(self, key):
        self._check_field(key)
        return get_value(self._delegate[key])

    def __setattr__(self, key, value):
        if key.startswith("_"):
            return super().__setattr__(key, value)

        self._check_field(key)
        self._delegate[key] = set_once(self._delegate[key], value)


class BaseInterface(BaseStruct):

    def __init__(self, upward_pipe, downward_pipe):
        super().__init__()

        self._engine = self.Engine(self, upward_pipe, downward_pipe)
        self._callbacks = {}


class BaseArray:

    def __init__(self):
        self.start = None
        self.end = None
        self.delegate = None

    def is_alloc(self):
        return self.delegate is not None

    def alloc(self, start, end):
        self.start = start
        self.end = end
        self.delegate = [None] * (1+end)

    def _check_key(self, key):
        if not self.is_alloc(): raise ValueError("not alloc'd")
        if not (self.start <= key <= self.end): raise KeyError("out of range")

    def __getitem__(self, index):
        self._check_key(index)
        return get_value(self.delegate[index])

    def __setitem__(self, index, value):
        self._check_key(index)
        self.delegate[index] = set_once(self.delegate[index], value)


def make_array(item_type):

    class Array(BaseArray):
        _item = item_type

    return Array


class Local:

    def __init__(self, interface):
        self._value = None
        self.interface = interface

    def is_set(self):
        return self._value is not None

    @property
    def value(self):
        return get_value(self._value)

    @value.setter
    def value(self, value):
        self._value = set_once(self._value, value)

