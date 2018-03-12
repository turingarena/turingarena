import importlib
import sys

import pkg_resources

from turingarena.problem.problem import make_problem


def form_evaluate(fields):
    problem_id = fields["problem"].value
    language = fields["language"].value
    source_text = fields["source_file"].value.decode()
    module_name, *rest = problem_id.split(":", 1)
    problem_module = importlib.import_module(module_name)
    if rest:
        [attr_name] = rest
        problem = getattr(problem_module, attr_name)
    else:
        problem_dir = pkg_resources.resource_filename(module_name, "")
        print(f"module_name: {module_name}, problem dir: {problem_dir!r}", file=sys.stderr)
        problem = make_problem(problem_dir)
    return problem.evaluate(source_text, language=language)
