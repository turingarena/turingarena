import importlib
from abc import abstractmethod
from collections import OrderedDict

from turingarena.make.node import EvaluationNode, EvaluationTask, EvaluationEntry


class EvaluationNodeProvider:
    __slots__ = []

    @abstractmethod
    def get_nodes(self):
        pass


def load_node_provider(name):
    module_name, qualname = name.split(":", 2)
    provider_module = importlib.import_module(module_name)
    return getattr(provider_module, qualname)


def load_plan(name):
    provider = load_node_provider(name)
    return resolve_plan(provider.get_nodes())


def resolve_plan(nodes):
    cache = OrderedDict()

    def dfs(node):
        try:
            cached = cache[node.name]
        except KeyError:
            pass
        else:
            assert cached == node
            return

        assert isinstance(node, EvaluationNode)
        if isinstance(node, EvaluationTask):
            for d in node.dependencies:
                dfs(d)

        cache[node.name] = node

    for t in nodes:
        dfs(t)
    return cache


def make_plan_signature(plan):
    return {
        "tasks": [
            {
                "name": node.name,
                "dependencies": [d.name for d in node.dependencies],
            }
            for node in plan.values()
            if isinstance(node, EvaluationTask)
        ],
        "entries": [
            {
                "name": node.name,
            }
            for node in plan.values()
            if isinstance(node, EvaluationEntry)
        ]
    }