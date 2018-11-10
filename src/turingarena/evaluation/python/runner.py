from contextlib import contextmanager

from turingarena.evaluation.runner import EvaluatorRunner
from . import wrapper


class PythonEvaluatorRunner(EvaluatorRunner):
    @contextmanager
    def perform_run(self):
        yield [
            self.params.python_executable or "python3",
            "-u",
            "-m",
            wrapper.__name__,
            "evaluator.py",
        ]
