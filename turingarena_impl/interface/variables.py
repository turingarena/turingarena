from collections import namedtuple

Variable = namedtuple("Variable", ["name", "dimensions"])
Reference = namedtuple("Reference", ["variable", "index_count"])
Allocation = namedtuple("Allocation", ["reference", "size"])
