from abc import abstractmethod


class ProtocolError(Exception):
    pass


class BaseAssignable:
    """
    Base class for data types to be used in assignable expressions.
    """

    @abstractmethod
    def on_get(self):
        """
        Returns the assigned value, or None if not yet defined.
        """

    @abstractmethod
    def on_set(self, value):
        """
        Sets the value.

        The parameter value cannot be None.
        """


def get_value_or_none(assignable):
    if isinstance(assignable, list):
        if None in assignable:
            raise ValueError("trying to read an area of an array that does not exist")
        return [get_value_or_none(v) for v in assignable]
    else:
        assert isinstance(assignable, BaseAssignable)
        return assignable.on_get()


def get_value(assignable):
    value = get_value_or_none(assignable)
    if value is None:
        raise ValueError("not set")
    return value


def set_value(assignable, value):
    if isinstance(assignable, list):
        for a, v in zip(assignable, value):
            if v is not None:
                set_value(a, v)
    else:
        assert isinstance(assignable, BaseAssignable)
        assignable.on_set(value)


class BaseArray(BaseAssignable):
    _item_type = None

    def __init__(self):
        assert issubclass(self._item_type, BaseAssignable)
        self.start = None
        self.delegate = None

    @property
    def size(self):
        """A pair (a, b) representing the interval (inclusive) of valid indexes.

        For empty intervals, the value is (a,a-1) for some chosen a
        """
        self.check_alloc()
        return len(self.delegate)

    @size.setter
    def size(self, value):
        if self.is_alloc():
            if value != self.size:
                raise ProtocolError(
                    "cannot change the range of an already alloc'd array")
            return

        self.delegate = [self._item_type() for _ in range(value)]

    @property
    def __len__(self):
        return self.size

    def is_alloc(self):
        return self.delegate is not None

    def on_get(self):
        return self

    def on_set(self, value):
        value = list(value)
        self.size = len(value)
        self[:] = value

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
        if not self.is_alloc():
            raise ValueError("not alloc'd")


def array(item_type):
    class Array(BaseArray):
        _item_type = item_type

    return Array


class BaseScalar(BaseAssignable):
    _base = None

    def __init__(self, value=None):
        self.value = None
        if value is not None:
            self.on_set(value)

    def on_get(self):
        return self.value

    def on_set(self, value):
        if not isinstance(value, self._base):
            raise TypeError("value {} has wrong type, expecting {}".format(value, self._base))

        if self.value is None:
            self.value = value
            return

        if self.value != value:
            raise ProtocolError(
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
