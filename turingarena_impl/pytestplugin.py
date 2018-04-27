import ast
import json
import os
import random
import re
import string
from functools import lru_cache

import pytest
from _pytest.assertion.rewrite import rewrite_asserts
from pytest import approx

from turingarena_impl.loader import make_dummy_package, split_module, find_package_path
from turingarena_impl.problem.python import HostPythonEvaluator


class EvaluationAssertionError(Exception):
    pass


class ProblemSolutionEvaluationItem(pytest.Item):
    def __init__(self, parent):
        super().__init__("evaluation", parent)

    def runtest(self):
        self.parent.evaluate(self)


class ProblemSolutionAssertionItem(pytest.Item):
    def __init__(self, parent, assertion):
        super().__init__(f"evaluation_assert {assertion}", parent)
        self.assertion = assertion

    def runtest(self):
        result = self.parent.evaluate(self)

        mode = "exec"
        tree = ast.parse(f"assert {self.assertion}\n", mode=mode)
        rewrite_asserts(tree)
        co = compile(tree, filename="<evaluation_assert>", mode=mode, dont_inherit=True)
        try:
            exec(co, dict(approx=approx), result._asdict())
        except AssertionError as e:
            raise EvaluationAssertionError(self.assertion) from e
        except Exception as e:
            raise AssertionError(f"exception while checking: {self.assertion}") from e

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
    def __init__(self, fspath, parent, evaluator_name, source_name):
        super().__init__(fspath=fspath, parent=parent)
        self.evaluator_name = evaluator_name
        self.source_name = source_name

    @lru_cache(None)
    def _do_evaluate(self):
        return HostPythonEvaluator(
            self.evaluator_name,
            interface_name=self.evaluator_name,
        ).evaluate(self.source_name)

    def evaluate(self, item):
        result = self._do_evaluate()
        item.add_report_section("call", "evaluation_stdout", "\n".join(result.stdout))
        item.add_report_section("call", "evaluation_result", json.dumps(result.data, indent=4))
        return result

    def load_assertion_in_source(self):
        mod, rel_path = split_module(self.source_name, default_arg="interface.txt")
        with open(find_package_path(mod, rel_path)) as f:
            source_text = f.read()
        return re.findall(r"evaluation_assert\s+(.+)", source_text)

    def collect(self):
        yield ProblemSolutionEvaluationItem(self)
        for assertion in self.load_assertion_in_source():
            yield ProblemSolutionAssertionItem(self, assertion)


def pytest_collect_file(path, parent):
    solutions_dir, source_filename = os.path.split(path)
    problem_dir, solutions_dirname = os.path.split(solutions_dir)

    if solutions_dirname != "solutions": return

    key = "".join(random.choices(string.ascii_lowercase, k=6))
    module_name = f"__turingarena_test_{key}"
    make_dummy_package(module_name, [problem_dir])

    return ProblemSolutionTestFile(
        fspath=path,
        parent=parent,
        evaluator_name=f"{module_name}",
        source_name=f"{module_name}:{path}",
    )
