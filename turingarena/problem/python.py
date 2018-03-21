import logging
import subprocess
import sys

from turingarena.interface.algorithm import Algorithm
from turingarena.problem.evaluator import ProblemEvaluator

logger = logging.getLogger(__name__)


class PythonEvaluator(ProblemEvaluator):
    __slots__ = ["script_path", "function_name"]

    def __init__(self, script_path, function_name="evaluate"):
        super().__init__(script_path=script_path, function_name=function_name)


class HostPythonEvaluator(PythonEvaluator):
    """
    Evaluates a Python problem in the host interpreter.
    """

    __slots__ = []

    def evaluate(self, algorithm_dir):
        print(self.script_path, self.function_name, algorithm_dir, file=sys.stderr)

        script_globals = {}
        with open(self.script_path) as f:
            script = compile(f.read(), self.script_path, mode="exec")
        exec(script, script_globals)

        script_globals[self.function_name](Algorithm(algorithm_dir))


class SubprocessPythonEvaluator(PythonEvaluator):
    """
    Evaluates a Python problem by launching an interpreter as subprocess.
    """

    __slots__ = []

    def evaluate(self, algorithm_dir):
        cli = [
            "python",
            "-m", __name__,
            self.script_path,
            self.function_name,
            algorithm_dir,
        ]
        logger.info(f"running {cli}")
        evaluation = subprocess.run(
            cli,
            check=True,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        return dict(
            stdout=evaluation.stdout,
        )


if __name__ == "__main__":
    script_path, function_name, algorithm_dir = sys.argv[1:]
    HostPythonEvaluator(script_path, function_name).evaluate(algorithm_dir)
