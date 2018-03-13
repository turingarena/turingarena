import sys

from turingarena.cli import docopt_cli
from turingarena.problem.problem import load_problem


@docopt_cli
def evaluate_cli(args):
    """Read a solution from stdin and evaluates it!

    Usage:
        evaluate [options]

    Options:
        -p --problem=<id>  Problem to evaluate [default: .]
        -x --language=<lang>  Language of the solution [default: c++]
    """

    source_text = sys.stdin.read()
    problem = load_problem(args["--problem"])
    evaluation = problem.evaluate(source_text, language=args["--language"])

    print(evaluation)
