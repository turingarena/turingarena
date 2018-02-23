import importlib
import logging
import os
import sys
from tempfile import TemporaryDirectory

from turingarena.cli import docopt_cli
from turingarena.common import ImmutableObject
from turingarena.protocol.proxy import ProxiedAlgorithm
from turingarena.sandbox.languages.cpp import CppAlgorithmSource


class EvaluationContext(ImmutableObject):
    __slots__ = [
        "algorithm",
        "logger",
        "feedback",
    ]


class FeedbackLogger:
    def send(self, severity, text):
        print(f"{severity}: {text}")

    def info(self, text):
        self.send("info", text)

    def success(self, text):
        self.send("success", text)

    def warning(self, text):
        self.send("warning", text)


class AlgorithmicProblem(ImmutableObject):
    __slots__ = [
        "interface",
        "checker",
    ]

    def evaluate(self, source):
        with TemporaryDirectory() as temp_dir:
            algorithm_dir = os.path.join(temp_dir, "algorithm")
            source.compile(algorithm_dir)

            context = EvaluationContext(
                algorithm=ProxiedAlgorithm(
                    algorithm_dir=algorithm_dir,
                    interface=self.interface,
                ),
                logger=logging.getLogger("evaluation"),
                feedback=FeedbackLogger(),
            )
            self.checker(context)


def algorithmic_problem(interface):
    def decorator(f):
        return AlgorithmicProblem(
            interface=interface,
            checker=f,
        )

    return decorator


@docopt_cli
def problem_evaluate_cli(args):
    """TuringArena problem evaluator.

    Usage:
        evaluate [options] <problem>
    """

    problem_module_name, problem_attr_name = args["<problem>"].split(":")
    problem_module = importlib.import_module(problem_module_name)
    problem = getattr(problem_module, problem_attr_name)

    source = CppAlgorithmSource(
        interface=problem.interface,
        language="c++",
        text=sys.stdin.read(),
        filename=None,
    )

    problem.evaluate(source)
