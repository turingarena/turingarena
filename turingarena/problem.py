import importlib
import os
import sys
from tempfile import TemporaryDirectory

from turingarena.cli import docopt_cli
from turingarena.common import ImmutableObject
from turingarena.interface.algorithm import Algorithm
from turingarena.interface.model.model import InterfaceDefinition
from turingarena.sandbox.sources import load_source


class AlgorithmicProblem(ImmutableObject):
    __slots__ = [
        "interface_text",
        "evaluator",
    ]

    def evaluate(self, source_text, *, language):
        interface = InterfaceDefinition.compile(self.interface_text)
        with TemporaryDirectory(dir="/dev/shm") as temp_dir:
            algorithm_dir = os.path.join(temp_dir, "algorithm")
            source = load_source(
                source_text,
                language=language,
                interface=interface,
            )
            source.compile(algorithm_dir=algorithm_dir)
            algorithm = Algorithm(algorithm_dir=algorithm_dir, interface=interface)

            self.evaluator(algorithm)


@docopt_cli
def problem_evaluate_cli(args):
    """TuringArena problem evaluator.

    Usage:
        evaluate [options]

    Options:
        -x --language=<lang>  Source language [default: c++].
        -I --interface=<file>  Interface definition file [default: interface.txt].
        -C --checker=<c>  Python module where the checker is located [default: problem:checker]
    """

    checker_module_name, checker_attr_name = args["--checker"].split(":")
    checker_module = importlib.import_module(checker_module_name)
    checker = getattr(checker_module, checker_attr_name)

    with open(args["--interface"]) as f:
        interface_text = f.read()

    problem = AlgorithmicProblem(
        interface_text=interface_text,
        evaluator=checker,
    )

    problem.evaluate(
        sys.stdin.read(),
        language=args["--language"],
    )
