import json
from contextlib import ExitStack

from turingarena.problem.problem import load_problem, clone_from_git
from turingarena.sandbox.languages.language import Language
from turingarena.sandbox.source import AlgorithmSource


def form_evaluate(fields):
    problem_name = fields["problem"].value
    language = Language.from_name(fields["language"].value)
    if "source_text" in fields:
        source_text = fields["source_text"].value
    else:
        source_text = fields["source_file"].value.decode()

    with ExitStack() as stack:
        try:
            git_url = fields["git_url"].value
        except KeyError:
            git_url = None
        if git_url:
            stack.enter_context(clone_from_git(git_url))

        problem = load_problem(problem_name)
        evaluation = problem.evaluate(AlgorithmSource.load(source_text, language=language, interface=problem.interface))
        return json.dumps(evaluation._asdict())
