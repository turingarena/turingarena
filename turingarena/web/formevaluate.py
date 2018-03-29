from turingarena.problem.problem import load_problem
from turingarena.sandbox.sources import load_source


def form_evaluate(fields):
    problem_name = fields["problem"].value
    language = fields["language"].value
    if "source_text" in fields:
        source_text = fields["source_text"].value
    else:
        source_text = fields["source_file"].value.decode()
    if problem_name == "git":
        problem = load_problem(".", git_url=fields["git_url"].value)
    else:
        problem = load_problem(problem_name)

    return problem.evaluate(load_source(source_text, language=language, interface=problem.interface))
