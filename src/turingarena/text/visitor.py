import functools


def xmlvisitormethod(f):
    @functools.wraps(f)
    def visitor(self, el):
        method = None
        if isinstance(el.tag, str):
            method = getattr(self, f"{f.__name__}_tag_{el.tag}", None)
            if method is None:
                method = getattr(self, f"{f.__name__}_tag", None)
        if method is None:
            method = getattr(self, f"{f.__name__}_node", None)
        if method is None:
            raise NotImplementedError(f"{f.__name__} for {el}")
        return method(el)

    return visitor


class TextVisitor:
    @xmlvisitormethod
    def visit(self, el):
        pass
