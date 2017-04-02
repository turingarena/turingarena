from collections import OrderedDict


def named_definitions(definitions):
    result = OrderedDict()
    for d in definitions:
        result[d.name] = d
    return result
