import logging
import subprocess
import sys

from turingarena.common import ImmutableObject
from turingarena.interface.algorithm import Algorithm

logger = logging.getLogger(__name__)


class PythonEvaluator(ImmutableObject):
    __slots__ = ["script_path", "function_name"]

    def __init__(self, script_path, function_name="evaluate"):
        super().__init__(script_path=script_path, function_name=function_name)

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
        return evaluation.stdout


def do_evaluate():
    script_path, function_name, algorithm_dir = sys.argv[1:]

    print(script_path, function_name, algorithm_dir, file=sys.stderr)

    script_globals = {}
    with open(script_path) as f:
        script = compile(f.read(), script_path, mode="exec")
    exec(script, script_globals)

    script_globals[function_name](Algorithm(algorithm_dir))


if __name__ == "__main__":
    do_evaluate()
