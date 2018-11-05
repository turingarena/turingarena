import collections
import logging
import numbers
from enum import IntEnum

logger = logging.getLogger(__name__)


class DriverState(IntEnum):
    READY = 0
    RESOURCE_USAGE = 1
    ERROR = -1


class MetaType(IntEnum):
    SCALAR = 0
    ARRAY = 1


def get_meta_type(value):
    if isinstance(value, collections.Iterable):
        return MetaType.ARRAY
    if isinstance(value, numbers.Integral):
        return MetaType.SCALAR
    raise AssertionError(f"unsupported type for value: {value}")


def serialize_data(value):
    meta_type = get_meta_type(value)
    yield meta_type.value
    if meta_type is MetaType.ARRAY:
        items = list(value)
        yield len(items)
        for item in items:
            yield from serialize_data(item)
    elif meta_type == MetaType.SCALAR:
        yield int(value)
    else:
        raise AssertionError


def deserialize_data():
    meta_type = MetaType(int((yield)))
    if meta_type is MetaType.ARRAY:
        size = int((yield))
        value = [None] * size
        for i in range(size):
            value[i] = yield from deserialize_data()
    elif meta_type == MetaType.SCALAR:
        value = int((yield))
    else:
        raise AssertionError
    return value
