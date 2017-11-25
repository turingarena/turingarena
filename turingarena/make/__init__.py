from collections import OrderedDict
from functools import partial

from turingarena.common import ImmutableObject


class Task(ImmutableObject):
    __slots__ = ["name", "target", "dependencies"]

    def __init__(self, target, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = target.__name__
        super().__init__(target=target, **kwargs)

    def get_tasks(self):
        return [self]


def resolve_plan(tasks):
    cache = OrderedDict()

    def dfs(node):
        try:
            cached = cache[node.name]
            assert cached == node
            return
        except KeyError:
            pass

        for d in node.dependencies:
            dfs(d)
        cache[node.name] = node

    for t in tasks:
        dfs(t)
    return cache


def task(*deps, **kwargs):
    return partial(Task, **kwargs, dependencies=list(deps))
