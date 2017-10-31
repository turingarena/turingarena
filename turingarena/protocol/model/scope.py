from collections import OrderedDict


class ScopeNamespace:
    __slots__ = ["parent", "delegate"]

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

    def items(self):
        if self.parent:
            yield from self.parent.items()
        yield from self.delegate.items()

    def values(self):
        if self.parent:
            yield from self.parent.values()
        yield from self.delegate.values()

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


class Scope:
    __slots__ = ["interfaces", "variables", "functions", "callbacks", "main"]

    def __init__(self, parent=None):
        for ns in Scope.__slots__:
            ns_parent = getattr(parent, ns) if parent else None
            setattr(self, ns, ScopeNamespace(ns_parent))

    def __repr__(self):
        names = ", ".join(
            k
            for ns in self.__slots__
            for k in getattr(self, ns).locals()
        )
        return f"Scope({names})"
