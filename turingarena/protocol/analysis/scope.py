class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.delegate = {}

    def locals(self):
        """Returns a _copy of_ this scope as a dict."""
        return dict(self.delegate)

    def __getitem__(self, key):
        try:
            return self.delegate[key]
        except KeyError:
            if self.parent:
                return self.parent[key]
            else:
                raise

    def __setitem__(self, key, value):
        if key in self.delegate:
            raise KeyError("already defined")
        self.delegate[key] = value
