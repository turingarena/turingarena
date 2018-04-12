import importlib
import importlib.util
import logging
from collections import namedtuple
from contextlib import redirect_stdout
from io import StringIO

from turingarena.algorithm import Algorithm
from turingarena.problem.evaluation import Evaluation

logger = logging.getLogger(__name__)


class HostPythonEvaluator(namedtuple("HostPythonEvaluator", [
    "module",
    "interface_name",
])):
    """
    Evaluates a Python problem in the host interpreter.
    Stdout is captured by changing sys.stdout.
    """

    __slots__ = []

    def evaluate(self, *, source_name, language_name):
        mod = importlib.import_module(".evaluate", self.module.__package__)

        eval_stdout = StringIO()
        with redirect_stdout(eval_stdout):
            algorithm = Algorithm(
                source_name=source_name,
                language_name=language_name,
                interface_name=self.interface_name,
            )
            data = mod.evaluate(algorithm)

        return Evaluation(
            stdout=eval_stdout.getvalue().splitlines(),
            data=data,
        )
