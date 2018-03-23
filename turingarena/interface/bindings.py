class BindingStorage:
    def __init__(self, *, local_variables, parent):
        self.local_variables = local_variables
        self.parent = parent
        self.values = {
            l: None for l in self.local_variables.values()
        }

    def __getitem__(self, variable):
        if variable in self.values:
            return self.values[variable]
        elif self.parent:
            return self.parent[variable]
        else:
            raise KeyError(variable)

    def __setitem__(self, variable, value):
        if variable in self.values:
            self.values[variable] = value
        elif self.parent:
            self.parent[variable] = value
        else:
            raise KeyError(variable)
