class Visitor:

    def visit(self, node):
        for cls in node.__class__.__mro__:
            try:
                method = getattr(self, f"visit_{cls.__name__}")
            except AttributeError:
                continue

            ans = method(node)
            if ans is not NotImplemented:
                return ans

        raise NotImplementedError(str(node.__class__))
