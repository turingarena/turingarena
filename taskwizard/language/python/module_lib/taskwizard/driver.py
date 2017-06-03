class Array:

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

    def _check_value(self, key):
        if not self.is_alloc(): raise ValueError("not alloc'd")
        if not (self.start <= key <= self.end): raise KeyError("out of range")

    def __getitem__(self, index):
        self._check_key(index)
        return self.delegate[index]

    def __setitem__(self, index, value):
        self._check_value(value)
        self.delegate[index] = value
