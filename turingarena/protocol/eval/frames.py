from contextlib import contextmanager


class Frame:
    __slots__ = ["scope_variables", "parent", "values"]

    def __init__(self, *, scope_variables, parent):
        self.scope_variables = scope_variables
        self.parent = parent
        self.values = {}


class RunContext:
    __slots__ = ["frames", "plumbing"]

    def __init__(self):
        self.frames = {}
        self.plumbing = set()

    @contextmanager
    def new_procelain_frame(self, scope_variables):
        assert scope_variables not in self.frames
        parent = self.frames[scope_variables.parent] if scope_variables.parent else None
        frame = self.frames[scope_variables] = Frame(
            scope_variables=scope_variables,
            parent=parent,
        )
        yield frame
        del self.frames[scope_variables]

    @contextmanager
    def new_plumbing_frame(self, scope_variables):
        assert scope_variables in self.frames
        assert scope_variables not in self.plumbing
        self.plumbing.add(scope_variables)
        yield self.frames[scope_variables]
        self.plumbing.remove(scope_variables)
