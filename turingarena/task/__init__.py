from collections import OrderedDict
from functools import partial

from turingarena.common import ImmutableObject


class Task(ImmutableObject):
    __slots__ = ["name", "target", "dependencies"]

    def __init__(self, target, **kwargs):
        kwargs.setdefault("name", target.__name__)
        super().__init__(target=target, **kwargs)

    def all_phases(self):
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

        dfs(self)
        return cache

    def run_phase(self, phase_name):
        self.all_phases()[phase_name].target()


def task(*deps, **kwargs):
    return partial(Task, **kwargs, dependencies=list(deps))
