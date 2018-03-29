import sys

from turingarena.cli import docopt_cli
from turingarena.problem.problem import load_problem
from turingarena.sandbox.sources import load_source


@docopt_cli
def evaluate_cli(args):
    """Read a solution from stdin and evaluates it!

    Usage:
        evaluate [options]

    Options:
        -p --problem=<id>  Problem to evaluate [default: .]
        -x --language=<lang>  Language of the solution [default: c++]
        -g --git=<url>  Clone problem from git
    """

    source_text = sys.stdin.read()
    if "--git" in args:
        git_url = args["--git"]
    else:
        git_url = None

    with load_problem(args["--problem"], git_url=git_url) as problem:
        evaluation = problem.evaluate(
            load_source(source_text, language=args["--language"], interface=problem.interface),
        )

    print(evaluation["stdout"])
