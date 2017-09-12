from abc import abstractmethod
from collections import deque
from functools import partial


class BaseStruct:
    def __init__(self):
        self._delegate = {}

        for k, t in self._fields.items():
            self._delegate[k] = t()

    def __getattr__(self, key):
        return self._delegate[key]


class BaseArray:

    _type = None

    def __init__(self):
        self.start = None
        self.end = None
        self.delegate = None

    def is_alloc(self):
        return self.delegate is not None

    def alloc(self, start, end):
        if self.is_alloc(): raise ValueError("already alloc'd")
        self.start = start
        self.end = end
        self.delegate = [self._item_type() for _ in range(end - start + 1)]

    @property
    def value(self):
        return self

    @value.setter
    def value(self, value):
        raise NotImplementedError

    def __getitem__(self, index):
        return self.delegate[self.resolve_index(index)].value

    def __setitem__(self, index, value):
        self.delegate[self.resolve_index(index)].value = value

    def resolve_index(self, index):
        if not self.is_alloc(): raise ValueError("not alloc'd")
        if not (self.start <= index <= self.end): raise IndexError("out of range")
        delegate_index = index - self.start
        return delegate_index


def array(item_type):
    class Array(BaseArray):
        _item_type = item_type

    return Array


class BaseScalar:
    def __init__(self):
        self._value = None

    def is_set(self):
        return self._value is not None

    @property
    def value(self):
        if not self.is_set(): raise ValueError("not set")
        return self._value

    @value.setter
    def value(self, value):
        if not self.is_set():
            self._value = value
            return

        if self._value == value: return
        raise ValueError(
            "cannot set to a different value ({previous} -> {new})".format(
                previous=self._value,
                new=value,
            )
        )


def scalar(base):
    class Scalar(BaseScalar):
        _base = base
    return Scalar


class Variable:

    def __init__(self, t, value=None):
        self._delegate = t()
        if value is not None:
            self._delegate.value = value

    def __getitem__(self, key):
        if key != slice(None, None, None):
            raise KeyError
        return self._delegate.value

    def __setitem__(self, key, value):
        if key != slice(None, None, None):
            raise KeyError
        self._delegate.value = value
