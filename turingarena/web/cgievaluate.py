"""
Evaluate a solution provided via a Web form.
"""
import cgi
import importlib
import sys
import traceback

import pkg_resources

from turingarena.problem.problem import make_problem


def evaluate():
    try:
        evaluation = do_evaluate()
    except:
        print("500 Internal Server Error")
        print()
        traceback.print_exc(file=sys.stdout)
        raise

    print("200 OK")
    print()
    print(evaluation)


def do_evaluate():
    fields = cgi.FieldStorage()
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
    evaluation = problem.evaluate(source_text, language=language)
    return evaluation


if __name__ == "__main__":
    evaluate()
