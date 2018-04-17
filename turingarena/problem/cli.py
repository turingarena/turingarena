import sys
from contextlib import ExitStack

from turingarena.cli import docopt_cli
from turingarena.problem.problem import clone_from_git
from turingarena.problem.python import HostPythonEvaluator
from turingarena.sandbox.languages.language import Language


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
        evaluator = HostPythonEvaluator(name=problem_name, interface_name=problem_name)
        language = Language.from_name(args["--language"])
        source_path = args["<source>"]
        evaluation = evaluator.evaluate(
            f":{source_path}",
            language=language,
        )

    print(evaluation.stdout)
    print(evaluation.data)
