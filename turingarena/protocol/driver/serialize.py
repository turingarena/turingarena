import collections
import numbers
from enum import IntEnum


class MetaType(IntEnum):
    SCALAR = 0
    ARRAY = 1


def get_meta_type(value):
    if isinstance(value, collections.Iterable):
        return MetaType.ARRAY
    if isinstance(value, numbers.Integral):
        return MetaType.SCALAR
    raise AssertionError(f"unsupported type for value: {value}")


def deserialize(lines):
    meta_type = MetaType(int(next(lines)))
    if meta_type is MetaType.ARRAY:
        size = int(next(lines))
        return [deserialize(lines) for _ in range(size)]
    elif meta_type == MetaType.SCALAR:
        return int(next(lines))
