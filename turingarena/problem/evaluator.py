from abc import abstractmethod


class ProblemEvaluator:
    __slots__ = []

    @abstractmethod
    def evaluate(self, *, prepared_problem_dir, submission_dir):
        pass
