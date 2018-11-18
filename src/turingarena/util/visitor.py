import functools


def visitormethod(f):
    @functools.wraps(f)
    def visitor_method(self, node):
        for cls in node.__class__.__mro__:
            try:
                method = getattr(self, f"{f.__name__}_{cls.__name__}")
            except AttributeError:
                continue

            ans = method(node)
            if ans is not NotImplemented:
                return ans

        raise NotImplementedError(str(node.__class__))

    return visitor_method


class Visitor:

    @visitormethod
    def visit(self, node):
        pass
