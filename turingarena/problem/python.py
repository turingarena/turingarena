import logging
import subprocess
import sys

from turingarena.interface.algorithm import Algorithm

logger = logging.getLogger(__name__)


class PythonEvaluator:
    def __init__(self, script_path, function_name="evaluate"):
        self.script_path = script_path
        self.function_name = function_name

    def evaluate(self, algorithm_dir):
        cli = [
            "python",
            "-m", __name__,
            self.script_path,
            self.function_name,
            algorithm_dir,
        ]
        logger.info("running {cli}")
        subprocess.run(
            cli,
            check=True,
        )


def do_evaluate():
    script_path, function_name, algorithm_dir = sys.argv[1:]

    script_globals = {}
    with open(script_path) as f:
        script = compile(f.read(), script_path, mode="exec")
    exec(script, script_globals)

    script_globals[function_name](Algorithm(algorithm_dir))


if __name__ == "__main__":
    do_evaluate()
