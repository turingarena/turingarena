from collections import namedtuple

VariableDeclaration = namedtuple("VariableDeclaration", ["name", "dimensions", "to_allocate"])
VariableAllocation = namedtuple("VariableAllocation", ["name", "dimensions", "indexes", "size"])


class Variable(namedtuple("Variable", ["name", "dimensions"])):
    pass


class DataReference(namedtuple("DataReference", ["variable", "indexes"])):
    pass
