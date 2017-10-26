from collections import namedtuple

scalar = namedtuple("scalar", ["base_type"])
array = namedtuple("array", ["item_type"])