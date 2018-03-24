import os

import pytest

from turingarena.problem.problem import make_problem, load_source_file


class ProblemSolutionTestItem(pytest.Item):
    def __init__(self, name, parent, problem, source):
        super().__init__(name, parent)
        self.problem = problem
        self.source = source

    def runtest(self):
        self.problem.evaluate(self.source)


def pytest_collect_file(path, parent):
    solutions_dir, source_filename = os.path.split(path)
    problem_dir, solutions_dirname = os.path.split(solutions_dir)

    if solutions_dirname != "solutions": return
    if not os.path.isfile(os.path.join(problem_dir, "interface.txt")): return

    problem = make_problem(problem_dir)
    source = load_source_file(
        solutions_dir,
        source_filename,
        interface=problem.interface,
    )

    return ProblemSolutionTestItem(
        name=str(path),
        parent=parent,
        problem=problem,
        source=source,
    )
