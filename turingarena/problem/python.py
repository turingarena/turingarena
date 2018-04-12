import importlib
import importlib.util
import logging
from collections import namedtuple
from contextlib import redirect_stdout
from io import StringIO

from turingarena.algorithm import Algorithm
from turingarena.loader import split_module
from turingarena.problem.evaluation import Evaluation
from turingarena.sandbox.languages.language import Language

logger = logging.getLogger(__name__)


class HostPythonEvaluator(namedtuple("HostPythonEvaluator", [
    "name",
    "interface_name",
])):
    """
    Evaluates a Python problem in the host interpreter.
    Stdout is captured by changing sys.stdout.
    """

    __slots__ = []

    def evaluate(self, source_name, *, language=None):
        if language is None:
            language = Language.from_source_name(source_name)

        mod, arg = split_module(self.name)
        assert arg is None
        evaluator_mod = importlib.import_module(".evaluate", mod.__package__)

        eval_stdout = StringIO()
        with redirect_stdout(eval_stdout):
            algorithm = Algorithm(
                source_name=source_name,
                language_name=language.name,
                interface_name=self.interface_name,
            )
            data = evaluator_mod.evaluate(algorithm)

        return Evaluation(
            stdout=eval_stdout.getvalue().splitlines(),
            data=data,
        )
