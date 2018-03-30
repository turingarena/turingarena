from contextlib import ExitStack

from turingarena.problem.problem import load_problem, clone_from_git
from turingarena.sandbox.sources import load_source


def form_evaluate(fields):
    problem_name = fields["problem"].value
    language = fields["language"].value
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
        return problem.evaluate(load_source(source_text, language=language, interface=problem.interface))
