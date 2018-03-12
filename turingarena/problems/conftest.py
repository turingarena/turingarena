import os

from turingarena.problem.problem import make_problem


def find_solutions(dirname):
    solutions_dir = os.path.join(dirname, "solutions")
    files = next(fs for r, ds, fs in os.walk(solutions_dir))
    langauge_by_extension = {
        ".cpp": "c++",
        ".py": "python",
        ".java": "java",
        ".js": "javascript",
    }
    for source_filename in files:
        base, ext = os.path.splitext(source_filename)
        source_path = os.path.join(solutions_dir, source_filename)
        with open(source_path) as f:
            source_text = f.read()
        yield base, ext, source_text, langauge_by_extension[ext]


def pytest_generate_tests(metafunc):
    module_dir = os.path.dirname(metafunc.module.__file__)

    if "problem" in metafunc.fixturenames:
        problems = {
            r: make_problem(r)
            for r, ds, fs in os.walk(module_dir)
            if "interface.txt" in fs
        }

        tests = {
            f"{os.path.basename(problem_dir)}/{base}/{ext[1:]}": (problem, source_text, language)
            for problem_dir, problem in problems.items()
            for base, ext, source_text, language in find_solutions(problem_dir)
        }

        metafunc.parametrize(
            "problem,source_text,language",
            list(tests.values()),
            ids=list(tests.keys()),
        )
