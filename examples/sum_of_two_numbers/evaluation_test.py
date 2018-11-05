import turingarena
from turingarena_impl.evaluation.evaluator import Evaluator
from turingarena_impl.evaluation.util import evaluation_text


def test_correct_solution():
    with turingarena.run_algorithm("solutions/correct.cpp") as p:
        assert p.functions.sum(3, 5) == 8


def test_evaluation():
    for line in evaluation_text(
            Evaluator(".").evaluate({"source": "solutions/correct.cpp"})
    ).splitlines():
        if not line:
            continue
        assert "correct" in line


def test_evaluation_wrong():
    for line in evaluation_text(
            Evaluator(".").evaluate({"source": "solutions/always_wrong.py"})
    ).splitlines():
        if not line:
            continue
        assert "WRONG" in line
