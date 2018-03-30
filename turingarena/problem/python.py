import json
import logging
import os
import subprocess
import sys
from contextlib import redirect_stdout
from io import StringIO

from turingarena.algorithm import Algorithm
from turingarena.common import ImmutableObject
from turingarena.problem.evaluation import Evaluation
from turingarena.problem.evaluator import ProblemEvaluator

logger = logging.getLogger(__name__)


class ProblemEvaluationContext(ImmutableObject):
    __slots__ = ["evaluation_dir"]

    @property
    def submission(self):
        return Algorithm(os.path.join(self.evaluation_dir, "submission"))

    @property
    def algorithms(self):
        root, dirs, files = next(os.walk(os.path.join(self.evaluation_dir, "algorithms")))
        return {
            name: Algorithm(os.path.join(root, name))
            for name in dirs
        }


class PythonEvaluator(ProblemEvaluator):
    __slots__ = ["script_path", "function_name"]

    def __init__(self, script_path, function_name="evaluate"):
        super().__init__(script_path=script_path, function_name=function_name)


class HostPythonEvaluator(PythonEvaluator):
    """
    Evaluates a Python problem in the host interpreter.
    Stdout is captured by changing sys.stdout.
    """

    __slots__ = []

    def evaluate(self, *, prepared_problem_dir, submission_dir):
        script_globals = {}
        with open(self.script_path) as f:
            script = compile(f.read(), self.script_path, mode="exec")

        context = ProblemEvaluationContext(prepared_problem_dir)
        script_globals["context"] = context

        eval_stdout = StringIO()
        with redirect_stdout(eval_stdout):
            exec(script, script_globals)
            data = script_globals[self.function_name](Algorithm(submission_dir))

        return Evaluation(stdout=eval_stdout.getvalue(), data=data)


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
