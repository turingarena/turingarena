from contextlib import contextmanager


class Frame:
    __slots__ = ["scope_variables", "parent", "values"]

    def __init__(self, *, scope_variables, parent):
        self.scope_variables = scope_variables
        self.parent = parent
        self.values = {
            l: None for l in self.scope_variables.locals().values()
        }

    def __getitem__(self, variable):
        if variable in self.values:
            return self.values[variable]
        elif self.parent:
            return self.parent[variable]
        else:
            raise KeyError

    def __setitem__(self, variable, value):
        if variable in self.values:
            self.values[variable] = value
        elif self.parent:
            self.parent[variable] = value
        else:
            raise KeyError


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
