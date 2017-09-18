from abc import abstractmethod


class ImmutabilityViolation(Exception):
    pass


class BaseAssignable:
    """
    Base class for data types to be used in assignable expressions.
    """

    @abstractmethod
    def on_get_value(self):
        pass

    @abstractmethod
    def on_set_value(self, value):
        pass


def get_value(assignable):
    if isinstance(assignable, list):
        return [get_value(v) for v in assignable]
    else:
        assert isinstance(assignable, BaseAssignable)
        return assignable.on_get_value()


def set_value(assignable, value):
    if isinstance(assignable, list):
        for a, v in zip(assignable, value):
            if value is not None:
                set_value(a, v)
    else:
        assert isinstance(assignable, BaseAssignable)
        assignable.on_set_value(value)


class RebasedList:
    """Wrapper to a list that specifies an initial index.

    Used to initialize non-zero-based arrays.
    """

    def __init__(self, start, items):
        self.start = start
        self.items = list(items)


def rebased(start, items):
    return RebasedList(start, items)


class BaseArray(BaseAssignable):
    _item_type = None

    def __init__(self):
        assert issubclass(self._item_type, BaseAssignable)
        self.start = None
        self.delegate = None

    @property
    def range(self):
        """A pair (a, b) representing the interval (inclusive) of valid indexes.

        For empty intervals, the value is (a,a-1) for some chosen a
        """
        self.check_alloc()
        return self.start, len(self.delegate) - 1

    @property
    def __len__(self):
        start, end = self.range
        return end - start + 1

    def is_alloc(self):
        return self.delegate is not None

    @range.setter
    def range(self, value):
        if self.is_alloc():
            if value != self.range:
                raise ImmutabilityViolation(
                    "cannot change the range of an already alloc'd array")
        start, end = value
        if start > end:
            raise ValueError("invalid range")
        self.start = start
        self.delegate = (
            [None for _ in range(start)] +
            [self._item_type() for _ in range(end - start + 1)]
        )

    def on_get_value(self):
        return self

    def on_set_value(self, value):
        if not isinstance(value, RebasedList):
            # by default lists are zero-based
            value = rebased(0, value)
        start = value.start
        self.range = (start, start + len(value.items) - 1)
        self[start:] = value.items

    def __getitem__(self, index):
        self.check_alloc()
        return get_value(self.delegate[index])

    def __setitem__(self, index, value):
        self.check_alloc()
        set_value(self.delegate[index], value)

    def __iter__(self):
        self.check_alloc()
        return iter(self.delegate[self.start:])

    def check_alloc(self):
        if not self.is_alloc(): raise ValueError("not alloc'd")


def array(item_type):
    class Array(BaseArray):
        _item_type = item_type

    return Array


class BaseScalar(BaseAssignable):
    _base = None

    def __init__(self, value=None):
        self.value = None
        if value is not None:
            self.on_set_value(value)

    def is_set(self):
        return self.value is not None

    def on_get_value(self):
        if not self.is_set():
            raise ValueError("not set")
        return self.value

    def on_set_value(self, value):
        if not isinstance(value, self._base):
            raise TypeError("value {} has wrong type, expecting {}".format(value, self._base))

        if not self.is_set():
            self.value = value
            return

        if self.value == value:
            return

        raise ImmutabilityViolation(
            "cannot set to a different value ({previous} -> {new})".format(
                previous=self.value,
                new=value,
            )
        )


def scalar(base):
    class Scalar(BaseScalar):
        _base = base

    return Scalar


class Variable:
    """
    Holds an assignable value, which is accessible through the self[:] notation.

    Used by generated protocol code to implement the assignable logic
    when writing/reading local variables,
    without cluttering the code too much.
    """

    def __init__(self, t):
        assert issubclass(t, BaseAssignable)
        self.delegate = t()

    def __getitem__(self, key):
        self.check_trivial_slice(key)
        return get_value(self.delegate)

    def __setitem__(self, key, value):
        self.check_trivial_slice(key)
        set_value(self.delegate, value)

    def check_trivial_slice(self, key):
        if key != slice(None, None, None):
            raise KeyError


def constant(t, value):
    v = Variable(t)
    v[:] = value
    return v
