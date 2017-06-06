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


class BaseInterface:

    def __init__(self, upward_pipe, downward_pipe):
        self.upward_pipe = upward_pipe
        self.downward_pipe = downward_pipe

        self.data = self.Data()

        self.preflight = self.make_preflight()
        self.downward = self.make_downward()
        self.upward = self.make_upward()
        self.postflight = self.make_postflight()

        self.downward_locals = deque()
        self.upward_locals = deque()
        self.postflight_locals = deque()

        next(self.preflight)
        next(self.upward)

    def make_local(self):
        local = Local(self)
        self.downward_locals.append(local)
        self.upward_locals.append(local)
        self.postflight_locals.append(local)
        return local

    def get_downward_local(self):
        return self.downward_locals.popleft()

    def get_upward_local(self):
        return self.upward_locals.popleft()

    def get_postflight_local(self):
        return self.postflight_locals.popleft()

    def call(self, name, *args):
        self.preflight.send((name, *args))

        next(self.downward)
        next(self.upward)

        return next(self.postflight)

    def read_upward(self, *types):
        raw_values = self.upward_pipe.readline().strip().split()
        return [t(value) for value, t in zip(raw_values, types)]

    def make_preflight(self):
        self.next_call = yield
        yield from self.preflight_protocol()

    def on_preflight_call(self):
        self.next_call = yield

    def get_next_call(self):
        return self.next_call

    @abstractmethod
    def preflight_protocol(self):
        pass

    def make_downward(self):
        yield from self.downward_protocol()

    @abstractmethod
    def downward_protocol(self):
        pass

    def on_downward_call(self):
        yield

    def make_upward(self):
        self.upward_called = True
        yield from self.upward_protocol()
        yield

    def on_upward_call(self):
        self.upward_called = True

    def on_upward_input(self):
        if self.upward_called:
            self.upward_called = False
            yield

    @abstractmethod
    def upward_protocol(self):
        pass

    def make_postflight(self):
        yield from self.postflight_protocol()

    @abstractmethod
    def postflight_protocol(self):
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
        if key.startswith("_"):
            return super().__getattr__(key)

        self._check_field(key)
        return get_value(self._delegate[key])

    def __setattr__(self, key, value):
        if key.startswith("_"):
            return super().__setattr__(key, value)

        self._check_field(key)
        self._delegate[key] = set_once(self._delegate[key], value)


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

