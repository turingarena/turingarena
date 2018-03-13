from turingarena.problem.problem import load_problem


def form_evaluate(fields):
    problem_name = fields["problem"].value
    language = fields["language"].value
    if "source_text" in fields:
        source_text = fields["source_text"].value
    else:
        source_text = fields["source_file"].value.decode()
    problem = load_problem(problem_name)
    return problem.evaluate(source_text, language=language)
