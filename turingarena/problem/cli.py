import os
import sys

from turingarena.cli import docopt_cli
from turingarena.problem.problem import make_problem


@docopt_cli
def evaluate_cli(args):
    """Read a solution from stdin and evaluates it!

    Usage:
        evaluate [options]

    Options:
        -p --problem=<id>  Problem to evaluate [default: .]
        -x --language=<lang>  Language of the solution [default: c++]
    """

    problems_dir = os.environ.get("TURINGARENA_PROBLEMS_PATH", ".")

    problem = make_problem(os.path.join(problems_dir, args["--problem"]))

    source_text = sys.stdin.read()

    evaluation = problem.evaluate(source_text, language=args["--language"])

    print(evaluation)
