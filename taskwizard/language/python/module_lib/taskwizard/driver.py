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
        self.downward = self._downward_protocol()
        self.downward.send(None)


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

    def __init__(self):
        self._value = None

    def is_set(self):
        return self._value is not None

    @property
    def value(self):
        return get_value(self._value)

    @value.setter
    def value(self, value):
        self._value = set_once(self._value, value)


def make_local():
    return Local()
