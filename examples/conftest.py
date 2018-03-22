import os

from turingarena.problem.problem import make_problem, find_algorithm_sources


def find_solutions(problem_dir, problem):
    for subdir in ["algorithms", "solutions"]:
        for name, source in find_algorithm_sources(
                os.path.join(problem_dir, subdir),
                interface=problem.interface,
        ):
            yield name, source


def pytest_generate_tests(metafunc):
    module_dir = os.path.dirname(metafunc.module.__file__)

    if "problem" in metafunc.fixturenames:
        problems = {
            r: make_problem(r)
            for r, ds, fs in os.walk(module_dir)
            if "interface.txt" in fs
        }

        tests = {
            f"{os.path.basename(problem_dir)}/{name}": (problem, source)
            for problem_dir, problem in problems.items()
            for name, source in find_solutions(problem_dir, problem)
        }

        metafunc.parametrize(
            "problem,source",
            list(tests.values()),
            ids=list(tests.keys()),
        )
