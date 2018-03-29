from turingarena.problem.problem import load_problem
from turingarena.sandbox.sources import load_source


def form_evaluate(fields):
    problem_name = fields["problem"].value
    language = fields["language"].value
    if "source_text" in fields:
        source_text = fields["source_text"].value
    else:
        source_text = fields["source_file"].value.decode()
    if "git_url" in fields:
        git_url = fields["git_url"]
    else:
        git_url = None
    problem = load_problem(problem_name, git_url=git_url)
    return problem.evaluate(load_source(source_text, language=language, interface=problem.interface))
