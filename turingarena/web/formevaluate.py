import json
import os
from contextlib import ExitStack
from tempfile import TemporaryDirectory

from turingarena.problem.problem import clone_from_git
from turingarena.problem.python import HostPythonEvaluator
from turingarena.sandbox.languages.language import Language


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

        temp_dir = stack.enter_context(TemporaryDirectory())
        source_path = os.path.join(temp_dir, f"source{language.extension}")
        with open(source_path, "x") as f:
            f.write(source_text)
        problem = HostPythonEvaluator(problem_name, interface_name=problem_name)
        evaluation = problem.evaluate(f":{source_path}")
        return json.dumps(evaluation._asdict())
