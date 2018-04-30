import sys
from contextlib import ExitStack

from turingarena_impl.cli import docopt_cli
from turingarena_impl.problem.problem import clone_from_git
from turingarena_impl.problem.python import HostPythonEvaluator


@docopt_cli
def evaluate_cli(args):
    """Read a solution from stdin and evaluates it!

    Usage:
        evaluate [options] <source>

    Options:
        -p --problem=<id>  Problem to evaluate
        -x --language=<lang>  Language of the solution [default: c++]
        -g --git=<url>  Clone problem from git
    """

    with ExitStack() as stack:
        git_url = args["--git"]
        if git_url is not None:
            stack.enter_context(clone_from_git(git_url))

        sys.path.append(".")
        problem_name = args["--problem"] or ""
        evaluator = HostPythonEvaluator(name=problem_name)
        source_path = args["<source>"]
        evaluation = evaluator.evaluate(
            f":{source_path}",
            language_name=args["--language"],
        )

    print(evaluation.stdout)
    print(evaluation.data)
