import importlib
import logging
import os
import sys
from tempfile import TemporaryDirectory

from turingarena.cli import docopt_cli
from turingarena.common import ImmutableObject
from turingarena.protocol.proxy.library import ProxiedAlgorithm
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
        "protocol_name",
        "interface_name",
        "checker",
    ]

    def evaluate(self, source):
        with TemporaryDirectory() as temp_dir:
            algorithm_dir = os.path.join(temp_dir, "algorithm")
            source.compile(algorithm_dir)

            context = EvaluationContext(
                algorithm=ProxiedAlgorithm(
                    algorithm_dir=algorithm_dir,
                    protocol_name=self.protocol_name,
                    interface_name=self.interface_name,
                ),
                logger=logging.getLogger("evaluation"),
                feedback=FeedbackLogger(),
            )
            self.checker(context)


def algorithmic_problem(protocol_name, interface_name):
    def decorator(f):
        return AlgorithmicProblem(
            protocol_name=protocol_name,
            interface_name=interface_name,
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
        protocol_name=problem.protocol_name,
        interface_name=problem.interface_name,
        language="c++",
        text=sys.stdin.read(),
        filename=None,
    )

    problem.evaluate(source)
