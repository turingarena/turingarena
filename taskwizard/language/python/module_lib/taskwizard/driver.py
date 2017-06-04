class BaseInterface:

    def __init__(self, upward_pipe, downward_pipe):
        self.upward_pipe = upward_pipe
        self.downward_pipe = downward_pipe
        self.data = self.Data()


class BaseStruct:

    def __init__(self):
        self._delegate = {}

        for k, t in self._fields.items():
            if issubclass(t, BaseArray):
                setattr(self, k, t())

    def __getattr__(self, key):
        if key.startswith("_"):
            return super().__getattr__(key)

        field = self._fields[key]
        if key not in self._delegate:
            raise ValueError("not set yet")
        return self._delegate[key]

    def __setattr__(self, key, value):
        if key.startswith("_"):
            return super().__setattr__(key, value)

        field = self._fields[key]
        if key in self._delegate:
            raise ValueError("already set")
        self._delegate[key] = value


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

    def _check_value(self, value):
        if value is None: raise ValueError

    def __getitem__(self, index):
        self._check_key(index)
        return self.delegate[index]

    def __setitem__(self, index, value):
        self._check_value(value)
        self.delegate[index] = value


def make_array(item_type):

    class Array(BaseArray):
        _item = item_type

    return Array
