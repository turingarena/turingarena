from abc import abstractmethod

from turingarena.common import ImmutableObject


class ProblemEvaluator(ImmutableObject):
    __slots__ = []

    @abstractmethod
    def evaluate(self, algorithm_dir):
        pass
