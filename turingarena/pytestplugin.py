import ast
import os
import re

import pytest
from _pytest.assertion.rewrite import rewrite_asserts
from future.moves import sys
from pytest import approx

from turingarena.problem.problem import load_source_file, load_problem


class EvaluationAssertionError(Exception):
    pass


class ProblemSolutionTestItem(pytest.Item):
    def __init__(self, parent, problem, source):
        super().__init__("test_solution", parent)
        self.problem = problem
        self.source = source

    def runtest(self):
        assertions = re.findall(r"evaluation_assert\s+(.+)", self.source.text)
        result = self.problem.evaluate(self.source)
        for condition in assertions:
            mode = "exec"
            tree = ast.parse(f"assert {condition}\n", mode=mode)
            rewrite_asserts(tree)
            co = compile(tree, filename="<evaluation_assert>", mode=mode, dont_inherit=True)
            try:
                exec(co, dict(approx=approx), result._asdict())
            except AssertionError as e:
                raise EvaluationAssertionError(condition) from e
            except Exception as e:
                raise AssertionError(f"exception while checking: {condition}") from e

    def repr_failure(self, excinfo):
        if isinstance(excinfo.value, EvaluationAssertionError):
            [condition] = excinfo.value.args
            return "\n".join([
                excinfo.value.__cause__.args[0],
                "",
                f"Failed evaluation assert: {condition}",
            ])
        return super().repr_failure(excinfo)


class ProblemSolutionTestFile(pytest.File):
    def __init__(self, fspath, parent, problem, source):
        super().__init__(fspath=fspath, parent=parent)
        self.problem = problem
        self.source = source

    def collect(self):
        yield ProblemSolutionTestItem(self, self.problem, self.source)


def pytest_collect_file(path, parent):
    solutions_dir, source_filename = os.path.split(path)
    problem_dir, solutions_dirname = os.path.split(solutions_dir)

    if solutions_dirname != "solutions": return

    if sys.path[0] != problem_dir:
        sys.path.insert(0, problem_dir)

    problem = load_problem()
    source = load_source_file(
        path,
        interface=problem.interface,
    )

    return ProblemSolutionTestFile(
        fspath=path,
        parent=parent,
        problem=problem,
        source=source,
    )
