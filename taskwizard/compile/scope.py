class Scope:

    def __init__(self, parent=None):
        if parent is None:
            self.delegate = {}
        else:
            self.delegate = parent.as_dict()

    def as_dict(self):
        """Returns a _copy of_ this scope as a dict."""
        return dict(self.delegate)

    def __getitem__(self, item):
        return self.delegate[item]

    def __setitem__(self, key, value):
        if key in self.delegate:
            raise KeyError("already defined")
        self.delegate[key] = value
