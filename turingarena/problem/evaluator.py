from abc import abstractmethod

from turingarena.common import ImmutableObject


class ProblemEvaluator(ImmutableObject):
    __slots__ = []

    @abstractmethod
    def evaluate(self, *, prepared_problem_dir, submission_dir):
        pass
