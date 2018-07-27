import ast
import os
import re

import pytest
from _pytest.assertion.rewrite import rewrite_asserts
from pytest import approx

from turingarena_impl.evaluation.evaluate import Evaluator
from turingarena_impl.evaluation.turingarena_tools import run_metaservers


class EvaluationAssertionError(Exception):
    pass


class EvaluationAssertionFailed(Exception):
    pass


class ProblemSolutionItem(pytest.Item):
    def __init__(self, parent):
        super().__init__(f"evaluation", parent)

    def load_assertion_in_source(self):
        with open(self.parent.source_path) as f:
            source_text = f.read()
        return re.findall(r"evaluation_assert\s+(.+)", source_text)

    def runtest(self):
        files = dict(source=self.parent.source_path)
        evaluator = Evaluator.get_evaluator(self.parent.evaluator_path)

        events = list(evaluator.evaluate(files))
        self.add_report_section("call", "evaluation", "\n".join(map(str, events)))

        for assertion in self.load_assertion_in_source():
            mode = "exec"
            tree = ast.parse(f"assert {assertion}\n", mode=mode)
            rewrite_asserts(tree)
            co = compile(tree, filename="<evaluation_assert>", mode=mode, dont_inherit=True)
            try:
                exec(co, dict(approx=approx), dict(evaluation=events))
            except AssertionError as e:
                raise EvaluationAssertionError(assertion) from e
            except Exception as e:
                raise EvaluationAssertionFailed(assertion) from e

    def repr_failure(self, excinfo):
        if isinstance(excinfo.value, EvaluationAssertionError):
            [condition] = excinfo.value.args
            return "\n".join([
                excinfo.value.__cause__.args[0],
                "",
                f"Failed evaluation assert: {condition}",
            ])
        if isinstance(excinfo.value, EvaluationAssertionFailed):
            [condition] = excinfo.value.args
            return "\n".join([
                excinfo.value.__cause__.args[0],
                "",
                f"Exception while checking evaluation assert: {condition}",
            ])
        return super().repr_failure(excinfo)


class ProblemSolutionTestFile(pytest.File):
    def __init__(self, fspath, parent, evaluator_path, source_path):
        super().__init__(fspath=fspath, parent=parent)
        self.evaluator_path = evaluator_path
        self.source_path = source_path

    def collect(self):
        yield ProblemSolutionItem(self)


def pytest_collect_file(path, parent):
    solutions_dir, source_filename = os.path.split(path)
    problem_dir, solutions_dirname = os.path.split(solutions_dir)
    evaluator_path = os.path.join(problem_dir, "evaluator.py")

    if solutions_dirname != "solutions": return

    return ProblemSolutionTestFile(
        fspath=path,
        parent=parent,
        evaluator_path=evaluator_path,
        source_path=path,
    )


@pytest.fixture(scope="session", autouse=True)
def turingarena_metaservers():
    with run_metaservers():
        yield
