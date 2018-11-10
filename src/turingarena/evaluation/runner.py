from abc import abstractmethod
from collections import namedtuple


class EvaluatorParameters:
    def __init__(self, params):
        self._params = params

    def __getattr__(self, item):
        return self._params.get(item)


class EvaluatorRunner(namedtuple("EvaluatorRunner", ["cwd", "path", "params"])):
    @abstractmethod
    def perform_run(self):
        """
        Returns a contextmanager which prepares the execution and gives the command to run.
        """
