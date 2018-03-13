import os
from tempfile import TemporaryDirectory

from turingarena.common import ImmutableObject
from turingarena.interface.interface import InterfaceDefinition
from turingarena.problem.python import PythonEvaluator
from turingarena.sandbox.sources import load_source


class AlgorithmicProblem(ImmutableObject):
    __slots__ = [
        "interface_text",
        "evaluator",
    ]

    def evaluate(self, source_text, *, language):
        interface = InterfaceDefinition.compile(self.interface_text)
        with TemporaryDirectory(dir="/tmp") as temp_dir:
            algorithm_dir = os.path.join(temp_dir, "algorithm")
            source = load_source(
                source_text,
                language=language,
                interface=interface,
            )
            source.compile(algorithm_dir=algorithm_dir)
            return self.evaluator.evaluate(algorithm_dir)


def make_problem(dirname):
    with open(os.path.join(dirname, "interface.txt")) as f:
        interface_text = f.read()

    return AlgorithmicProblem(
        interface_text=interface_text,
        evaluator=PythonEvaluator(script_path=os.path.join(dirname, "evaluate.py"))
    )
