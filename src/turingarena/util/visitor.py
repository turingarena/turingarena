import functools
from functools import partial


def visitormethod(f, *, meta=False, static=False):
    @functools.wraps(f)
    def visitor_method(self, node, *args, **kwargs):
        if meta:
            mro = node.__mro__
        else:
            mro = node.__class__.__mro__

        for cls in mro:
            try:
                method = getattr(self, f"{f.__name__}_{cls.__name__}")
            except AttributeError:
                continue

            if static:
                ans = method(*args, **kwargs)
            else:
                ans = method(node, *args, **kwargs)

            if ans is not NotImplemented:
                return ans

        options = ", ".join(cls.__name__ for cls in mro)
        raise NotImplementedError(f"{f.__name__} for [{options}]")

    return visitor_method


classvisitormethod = partial(visitormethod, meta=True)


class Visitor:

    @visitormethod
    def visit(self, node):
        pass
