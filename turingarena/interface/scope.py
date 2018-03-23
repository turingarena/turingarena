from collections import OrderedDict


class ScopeNamespace:
    __slots__ = ["parent", "delegate"]

    def __init__(self, parent=None):
        self.parent = parent
        self.delegate = OrderedDict()

    def locals(self):
        """Returns a _copy of_ this scope as a dict."""
        return OrderedDict(self.delegate)

    def __bool__(self):
        return bool(len(self))

    def __len__(self):
        ans = len(self.delegate)
        if self.parent:
            ans += len(self.parent)
        return ans

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
            if not self.parent:
                raise
        return self.parent[key]

    def __setitem__(self, key, value):
        if key in self.delegate:
            raise KeyError("already defined")
        self.delegate[key] = value


class Scope:
    namespaces = ["variables", "functions"]
    __slots__ = namespaces + ["parent"]

    def __init__(self, parent=None):
        self.parent = parent
        for ns in Scope.namespaces:
            ns_parent = getattr(parent, ns) if parent else None
            setattr(self, ns, ScopeNamespace(ns_parent))

    def __repr__(self):
        names = ", ".join(
            k
            for ns in self.namespaces
            for k in getattr(self, ns).locals()
        )
        return f"Scope({names})"
