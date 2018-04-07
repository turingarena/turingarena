import sys
from contextlib import ExitStack

from turingarena.cli import docopt_cli
from turingarena.problem.problem import load_problem, clone_from_git
from turingarena.sandbox.languages.language import Language
from turingarena.sandbox.source import AlgorithmSource


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

    with ExitStack() as stack:
        git_url = args["--git"]
        if git_url is not None:
            stack.enter_context(clone_from_git(git_url))

        sys.path.append(".")
        problem = load_problem(args["--problem"])
        language = Language.from_name(args["--language"])
        evaluation = problem.evaluate(
            AlgorithmSource.load(
                sys.stdin.read(),
                language=language,
                interface=problem.interface,
            ),
        )

    print(evaluation.stdout)
    print(evaluation.data)
