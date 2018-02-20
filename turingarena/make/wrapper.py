from abc import abstractmethod
from functools import partial

from turingarena.make.node import EvaluationTask, EvaluationEntry
from turingarena.make.plan import EvaluationNodeProvider


class EvaluationNodeWrapper(EvaluationNodeProvider):
    __slots__ = ["target", "node"]

    def __init__(self, target, **kwargs):
        self.target = target
        name = f"{target.__module__}:{target.__qualname__}"
        self.node = self.make_node(name, target, **kwargs)

    @abstractmethod
    def make_node(self, name, target, **kwargs):
        pass

    def get_nodes(self):
        return [self.node]


class EvaluationTaskWrapper(EvaluationNodeWrapper):
    __slots__ = []

    def make_node(self, name, target, **kwargs):
        return EvaluationTask(name=name, target=target, **kwargs)


class EvaluationEntryWrapper(EvaluationNodeProvider):
    __slots__ = []

    def make_node(self, name, target, **kwargs):
        return EvaluationEntry(name=name, **kwargs)


def task(*deps, **kwargs):
    return partial(EvaluationTaskWrapper, **kwargs, dependencies=list(deps))


def entry(**kwargs):
    return partial(EvaluationEntryWrapper, **kwargs)
