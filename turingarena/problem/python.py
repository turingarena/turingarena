import importlib
import importlib.util
import json
import logging
import subprocess
import sys
from collections import namedtuple
from contextlib import redirect_stdout
from io import StringIO

from turingarena.algorithm import Algorithm
from turingarena.problem.evaluation import Evaluation
from turingarena.problem.evaluator import ProblemEvaluator

logger = logging.getLogger(__name__)


class PythonEvaluator(ProblemEvaluator, namedtuple("PythonEvaluator", [
    "script_path", "function_name"
])):
    __slots__ = []

    def __new__(cls, script_path, function_name="evaluate"):
        return super().__new__(cls, script_path=script_path, function_name=function_name)


class HostPythonEvaluator(namedtuple("HostPythonEvaluator", ["module"])):
    """
    Evaluates a Python problem in the host interpreter.
    Stdout is captured by changing sys.stdout.
    """

    __slots__ = []

    def evaluate(self, *, prepared_problem_dir, submission_dir):
        mod = importlib.import_module(".evaluate", self.module.__package__)

        eval_stdout = StringIO()
        with redirect_stdout(eval_stdout):
            data = mod.evaluate(Algorithm(submission_dir))

        return Evaluation(
            stdout=eval_stdout.getvalue().splitlines(),
            data=data,
        )


class SubprocessPythonEvaluator(PythonEvaluator):
    """
    Evaluates a Python problem by launching an interpreter as subprocess.
    """

    __slots__ = []

    def evaluate(self, *, prepared_problem_dir, submission_dir):
        cli = [
            "python",
            "-m", __name__,
            self.script_path,
            self.function_name,
            prepared_problem_dir,
            submission_dir,
        ]
        logger.info(f"running {cli}")
        process = subprocess.run(
            cli,
            check=True,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        return Evaluation(**json.loads(process.stdout))


if __name__ == "__main__":
    script_path, function_name, prepared_problem_dir, submission_dir = sys.argv[1:]
    evaluation = HostPythonEvaluator(script_path, function_name).evaluate(
        prepared_problem_dir=prepared_problem_dir,
        submission_dir=submission_dir,
    )
    json.dump(evaluation._asdict(), fp=sys.stdout)
