from collections import OrderedDict


class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.delegate = OrderedDict()

    def locals(self):
        """Returns a _copy of_ this scope as a dict."""
        return OrderedDict(self.delegate)

    def __iter__(self):
        if self.parent:
            yield from self.parent
        yield from self.delegate

    def __getitem__(self, key):
        self.check_key(key)
        try:
            return self.delegate[key]
        except KeyError:
            if self.parent:
                return self.parent[key]
            else:
                raise

    def __setitem__(self, key, value):
        self.check_key(key)
        if key in self.delegate:
            raise KeyError("already defined")
        self.delegate[key] = value

    def check_key(self, key):
        _, _ = key
